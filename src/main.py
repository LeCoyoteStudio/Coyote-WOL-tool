# -*- coding: utf-8 -*-

# ==============================================================================
# CoyoteWOLtool - Serveur API principal
#
# Basé sur Flask, ce script fournit une API RESTful et sert l'interface web
# pour scanner et réveiller des appareils sur le réseau local.
# ==============================================================================

import sqlite3
import datetime
import socket
import os
import re
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, render_template, abort

# --- Configuration de l'application ---
PACKAGE_NAME = "CoyoteWOLtool"
# Chemin absolu vers le répertoire des données persistantes
VAR_DIR = f"/var/packages/{PACKAGE_NAME}/var"
# Chemin vers la base de données SQLite
DB_FILE = os.path.join(VAR_DIR, "devices.db")
# Port d'écoute du serveur web
APP_PORT = 9989
# Fichier de log
LOG_FILE = f"/var/log/{PACKAGE_NAME}.log"

# --- Configuration de la journalisation (logging) ---
# Met en place un logger robuste qui écrit dans un fichier avec rotation
# pour éviter que le fichier de log ne devienne trop gros.
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=5) # 1MB par fichier, 5 fichiers max
log_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# --- Initialisation de l'application Flask ---
# CORRECTION : Les chemins vers les templates et les fichiers statiques sont maintenant
# relatifs au script main.py, car ils sont dans le même dossier 'src'.
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- Internationalisation (i18n) ---
# Un système simple pour les traductions.
translations = {
    'en': {
        'invalid_mac': "Invalid MAC address format.",
        'packet_sent': "Magic packet sent to {mac}.",
        'generic_error': "An internal error occurred: {error}",
        'invalid_ip': "Invalid IP address format.",
        'device_not_found': "Device with MAC {mac} not found.",
        'update_success': "Device {mac} updated successfully."
    },
    'fr': {
        'invalid_mac': "Format d'adresse MAC invalide.",
        'packet_sent': "Paquet magique envoyé à {mac}.",
        'generic_error': "Une erreur interne est survenue : {error}",
        'invalid_ip': "Format d'adresse IP invalide.",
        'device_not_found': "Appareil avec la MAC {mac} non trouvé.",
        'update_success': "Appareil {mac} mis à jour avec succès."
    },
    # Ajoutez d'autres langues ici (es, de, etc.)
}

def get_locale():
    """Détermine la langue à utiliser à partir des arguments ou des en-têtes."""
    lang = request.args.get('lang')
    if lang and lang in translations:
        return lang
    # Fallback sur l'en-tête 'Accept-Language' du navigateur
    return request.accept_languages.best_match(translations.keys()) or 'en'

def _(key, **kwargs):
    """Fonction de traduction principale."""
    locale = get_locale()
    return translations.get(locale, translations['en']).get(key, key).format(**kwargs)

# --- Fonctions utilitaires ---
def get_db_connection():
    """Établit et retourne une connexion à la base de données SQLite."""
    try:
        conn = sqlite3.connect(DB_FILE)
        # Permet d'accéder aux colonnes par leur nom.
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def validate_mac_address(mac):
    """Vérifie si une chaîne est une adresse MAC valide."""
    return re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac)

def validate_ip_address(ip):
    """Vérifie si une chaîne est une adresse IP v4 valide."""
    return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip)

def send_wol_packet(mac_address: str):
    """Construit et envoie un paquet magique Wake-on-LAN."""
    if not validate_mac_address(mac_address):
        raise ValueError(_('invalid_mac'))
    
    # Nettoie l'adresse MAC et la convertit en bytes.
    mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
    
    # Le paquet magique est composé de 6 bytes FF suivis de 16 répétitions de l'adresse MAC.
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Envoie le paquet en broadcast sur le port 9 (standard pour WOL).
        s.sendto(magic_packet, ('<broadcast>', 9))
    logger.info(f"WOL packet sent to {mac_address}")

# --- Gestionnaires d'erreurs globaux ---
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": _('generic_error', error=str(error))}), 500

# --- Route principale pour l'interface Web ---
@app.route('/')
def index():
    """Sert la page HTML principale de l'application."""
    return render_template('index.html')

# ==============================================================================
# --- Endpoints de l'API RESTful ---
# ==============================================================================

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Récupère la liste des appareils depuis la base de données."""
    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed.")
        
    try:
        # Ne récupère que les appareils vus dans les 90 derniers jours pour garder la liste propre.
        ninety_days_ago = datetime.datetime.now() - datetime.timedelta(days=90)
        cursor = conn.cursor()
        devices = cursor.execute(
            '''SELECT mac, ip, hostname, last_seen, custom_name, is_favorite
               FROM devices WHERE last_seen >= ?
               ORDER BY is_favorite DESC, last_seen DESC''',
            (ninety_days_ago,)
        ).fetchall()
        conn.close()
        # Convertit les objets Row en dictionnaires pour la sérialisation JSON.
        return jsonify([dict(row) for row in devices])
    except sqlite3.Error as e:
        logger.error(f"API /devices - Database error: {e}")
        abort(500, description=str(e))

@app.route('/api/device/<string:mac>', methods=['PUT'])
def update_device(mac):
    """Met à jour les informations d'un appareil (nom, favori)."""
    if not validate_mac_address(mac):
        return jsonify({"error": _('invalid_mac')}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    conn = get_db_connection()
    if not conn:
        abort(500, description="Database connection failed.")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT mac FROM devices WHERE mac = ?", (mac,))
        if not cursor.fetchone():
            return jsonify({"error": _('device_not_found', mac=mac)}), 404

        custom_name = data.get('custom_name')
        is_favorite = data.get('is_favorite')

        cursor.execute(
            "UPDATE devices SET custom_name = ?, is_favorite = ? WHERE mac = ?",
            (custom_name, is_favorite, mac)
        )
        conn.commit()
        conn.close()
        
        logger.info(f"Updated device {mac} with data: {data}")
        return jsonify({"status": "success", "message": _('update_success', mac=mac)})
    except sqlite3.Error as e:
        logger.error(f"API /device/{mac} - Database error: {e}")
        abort(500, description=str(e))

@app.route('/api/ping/<string:ip_address>', methods=['GET'])
def ping_device(ip_address):
    """Vérifie si un appareil est en ligne en utilisant la commande ping."""
    if not validate_ip_address(ip_address):
        return jsonify({"status": "error", "message": _('invalid_ip')}), 400
    
    try:
        # Utilise ping avec un timeout de 1 seconde (-W 1) et un seul paquet (-c 1).
        # Redirige la sortie pour ne pas polluer les logs.
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', ip_address],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        status = "online" if result.returncode == 0 else "offline"
        return jsonify({"status": status})
    except Exception as e:
        logger.error(f"Ping command failed for {ip_address}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/wakeup', methods=['POST'])
def wakeup_device():
    """Déclenche l'envoi d'un paquet Wake-on-LAN."""
    mac = request.get_json().get('mac')
    if not mac:
        return jsonify({"status": "error", "message": "MAC address is required."}), 400
        
    try:
        send_wol_packet(mac)
        return jsonify({"status": "success", "message": _('packet_sent', mac=mac)})
    except ValueError as e:
        # Erreur de validation de l'adresse MAC.
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        # Autres erreurs (ex: réseau).
        logger.error(f"Wake-on-LAN failed for {mac}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Lancement du serveur ---
if __name__ == '__main__':
    logger.info(f"Starting {PACKAGE_NAME} server on port {APP_PORT}")
    # 'debug=False' est crucial pour la production.
    # 'host=0.0.0.0' permet au serveur d'être accessible depuis l'extérieur du conteneur.
    app.run(host='0.0.0.0', port=APP_PORT, debug=False)
