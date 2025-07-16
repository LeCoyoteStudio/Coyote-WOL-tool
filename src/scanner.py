import sqlite3
import datetime
import os
import sys
from scapy.all import srp, Ether, ARP, conf

PACKAGE_NAME = "CoyoteWOLtool"
DB_PATH = f"/var/packages/{PACKAGE_NAME}/var"
DB_FILE = os.path.join(DB_PATH, "devices.db")

def get_network_range():
    """Détermine la plage réseau locale (ex: 192.168.1.0/24)."""
    try:
        # Utilise la configuration de Scapy pour trouver l'interface et le réseau
        iface = conf.iface
        ip_addr = iface.ip
        netmask = iface.netmask
        
        # Calcul de l'adresse réseau
        ip_parts = list(map(int, ip_addr.split('.')))
        mask_parts = list(map(int, netmask.split('.')))
        net_addr_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
        network_address = ".".join(map(str, net_addr_parts))

        # Calcul du CIDR
        cidr = sum(bin(part).count('1') for part in mask_parts)
        
        return f"{network_address}/{cidr}"
    except Exception as e:
        print(f"Could not determine network range automatically, falling back to 192.168.1.0/24. Error: {e}")
        return "192.168.1.0/24"

def init_db():
    """Initialise ou met à jour le schéma de la base de données."""
    os.makedirs(DB_PATH, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    try:
        cursor.execute('ALTER TABLE devices ADD COLUMN custom_name TEXT')
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE devices ADD COLUMN is_favorite INTEGER DEFAULT 0')
    except sqlite3.OperationalError: pass
    conn.commit()
    conn.close()
    print("Database initialized/updated successfully.")

def scan_network():
    """Scanne le réseau avec Scapy et met à jour la base de données."""
    init_db()
    network_range = get_network_range()
    print(f"Scanning network with Scapy on range: {network_range}...")
    
    try:
        # Création d'un paquet ARP pour demander "qui a cette IP ?"
        arp_request = ARP(pdst=network_range)
        # Création d'une trame Ethernet pour diffuser la requête
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request

        # Envoi des paquets et réception des réponses
        # timeout=2 signifie qu'on attend 2 secondes pour les réponses
        answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        now = datetime.datetime.now()

        print(f"Found {len(answered_list)} devices.")
        for sent, received in answered_list:
            ip = received.psrc
            mac = received.hwsrc.upper()
            hostname = 'N/A' # L'ARP ne fournit pas de nom d'hôte

            cursor.execute("SELECT mac FROM devices WHERE mac = ?", (mac,))
            if cursor.fetchone():
                cursor.execute('UPDATE devices SET ip = ?, hostname = ?, last_seen = ? WHERE mac = ?', (ip, hostname, now, mac))
            else:
                cursor.execute('INSERT INTO devices (mac, ip, hostname, last_seen) VALUES (?, ?, ?, ?)', (mac, ip, hostname, now))

        conn.commit()
        conn.close()
        print("Scapy scan complete and database updated.")

    except Exception as e:
        print(f"An unexpected error occurred during Scapy scan: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--init-db':
        init_db()
    else:
        scan_network()
