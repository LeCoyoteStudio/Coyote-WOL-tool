# -*- coding: utf-8 -*-

# ==============================================================================
# CoyoteWOLtool - Scanner Réseau
#
# Ce script est conçu pour être exécuté périodiquement (via une tâche cron)
# pour scanner le réseau local, découvrir les appareils actifs et mettre à jour
# la base de données SQLite.
# ==============================================================================

import sqlite3
import datetime
import os
import sys
import logging
import subprocess
from logging.handlers import RotatingFileHandler
from scapy.all import srp, Ether, ARP, conf

# --- Configuration ---
PACKAGE_NAME = "CoyoteWOLtool"
VAR_DIR = f"/var/packages/{PACKAGE_NAME}/var"
DB_FILE = os.path.join(VAR_DIR, "devices.db")
LOG_FILE = f"/var/log/{PACKAGE_NAME}.log"

# --- Configuration de la journalisation (logging) ---
# Utilise le même fichier de log que le serveur web pour une centralisation.
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [Scanner] %(message)s')
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=5)
log_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def get_network_range():
    """
    Tente de déterminer la plage réseau locale (ex: 192.168.1.0/24).
    Utilise la commande `ip route` qui est plus standard sur les systèmes Linux.
    """
    try:
        # Exécute la commande 'ip route' et récupère la première ligne contenant 'default'
        result = subprocess.run(
            "ip route | grep default",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        # Extrait l'interface (ex: 'eth0')
        interface = result.stdout.split()[4]
        
        # Exécute 'ip addr show' pour trouver l'adresse CIDR de cette interface
        result = subprocess.run(
            f"ip addr show {interface} | grep 'inet '",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        # Extrait l'adresse CIDR (ex: '192.168.1.10/24')
        cidr_address = result.stdout.strip().split()[1]
        logger.info(f"Successfully determined network range: {cidr_address}")
        return cidr_address
    except Exception as e:
        fallback_range = "192.168.1.0/24"
        logger.warning(f"Could not determine network range automatically. Error: {e}. Falling back to {fallback_range}")
        return fallback_range

def get_hostname_from_ip(ip_address):
    """Tente de résoudre le nom d'hôte d'une adresse IP via nslookup."""
    try:
        # nslookup est un outil de diagnostic DNS standard.
        result = subprocess.run(
            ['nslookup', ip_address],
            capture_output=True,
            text=True,
            timeout=2
        )
        if "name =" in result.stdout:
            # Extrait le nom d'hôte de la sortie.
            hostname = result.stdout.split('name =')[-1].strip().rstrip('.')
            return hostname
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.warning(f"Could not resolve hostname for {ip_address}: {e}")
    return None

def init_db():
    """
    Initialise la base de données si elle n'existe pas, ou met à jour le schéma
    de la table si de nouvelles colonnes sont nécessaires.
    """
    logger.info("Initializing database...")
    try:
        os.makedirs(VAR_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Crée la table si elle n'existe pas.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                mac TEXT PRIMARY KEY,
                ip TEXT,
                hostname TEXT,
                last_seen TIMESTAMP,
                custom_name TEXT,
                is_favorite INTEGER DEFAULT 0
            )
        ''')
        
        # Ajoute les colonnes si elles manquent (pour les mises à jour).
        # Ces commandes échouent sans erreur si la colonne existe déjà.
        try:
            cursor.execute('ALTER TABLE devices ADD COLUMN custom_name TEXT')
        except sqlite3.OperationalError: pass
        try:
            cursor.execute('ALTER TABLE devices ADD COLUMN is_favorite INTEGER DEFAULT 0')
        except sqlite3.OperationalError: pass
        
        conn.commit()
        conn.close()
        logger.info("Database initialized/updated successfully.")
    except Exception as e:
        logger.error(f"FATAL: Could not initialize database at {DB_FILE}. Error: {e}")
        sys.exit(1) # Quitte le script si la BDD n'est pas accessible.

def scan_and_update():
    """
    Fonction principale qui scanne le réseau et met à jour la base de données.
    """
    logger.info("--- Starting network scan ---")
    network_range = get_network_range()
    
    try:
        # Prépare un paquet ARP (Address Resolution Protocol) pour demander "qui a cette IP ?".
        # Le paquet est envoyé en broadcast (à tout le monde sur le réseau).
        arp_request = ARP(pdst=network_range)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request

        # Envoie les paquets et attend les réponses pendant 2 secondes.
        answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

        if not answered_list:
            logger.info("Scan complete. No active devices found.")
            return

        logger.info(f"Scan complete. Found {len(answered_list)} active devices.")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.datetime.now()

        for sent, received in answered_list:
            ip = received.psrc
            mac = received.hwsrc.upper()

            cursor.execute("SELECT ip, hostname FROM devices WHERE mac = ?", (mac,))
            result = cursor.fetchone()
            
            # Tente de récupérer le nom d'hôte.
            hostname = get_hostname_from_ip(ip)

            if result:
                # L'appareil est déjà connu, on met à jour ses informations.
                # On ne met à jour le nom d'hôte que s'il n'y en avait pas ou si on en trouve un meilleur.
                current_hostname = result[1]
                if hostname and current_hostname in [None, 'N/A', '']:
                    update_query = 'UPDATE devices SET ip = ?, hostname = ?, last_seen = ? WHERE mac = ?'
                    cursor.execute(update_query, (ip, hostname, now, mac))
                else:
                    update_query = 'UPDATE devices SET ip = ?, last_seen = ? WHERE mac = ?'
                    cursor.execute(update_query, (ip, now, mac))
            else:
                # C'est un nouvel appareil, on l'insère dans la base.
                insert_query = 'INSERT INTO devices (mac, ip, hostname, last_seen) VALUES (?, ?, ?, ?)'
                cursor.execute(insert_query, (mac, ip, hostname or 'N/A', now))

        conn.commit()
        conn.close()
        logger.info("Database successfully updated with scan results.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during network scan: {e}")

if __name__ == "__main__":
    # La logique principale est déclenchée par les arguments passés au script.
    if len(sys.argv) > 1 and sys.argv[1] == '--init-db':
        init_db()
    else:
        # Avant de scanner, on s'assure que la BDD est prête.
        init_db()
        scan_and_update()
