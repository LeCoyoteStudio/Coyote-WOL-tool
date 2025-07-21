# Rôle : Cœur de l'application. Contient le serveur Flask, l'API et la logique métier.
import os
import sys
import threading
import time
import json
import sqlite3
import subprocess

# --- Ajout des dépendances "vendored" au path de Python ---
# Permet d'importer les bibliothèques incluses dans le paquet (Flask, Scapy, etc.)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))

from flask import Flask, jsonify, request, send_from_directory, Response
from scapy.all import srp, Ether, ARP, conf, get_if_addr, get_if_net, sr1, IP, ICMP

# --- Configuration ---
PACKAGE_ROOT = '/var/packages/coyotewol/target'
DATABASE_FILE = os.path.join(PACKAGE_ROOT, 'coyote_wol.db')
SCAN_INTERVAL_SECONDS = 600  # 10 minutes
DEVICE_EXPIRATION_DAYS = 90

# --- Initialisation de l'App ---
app = Flask(__name__)

# --- Gestion de la Base de Données ---
def init_db():
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            mac TEXT PRIMARY KEY,
            ip TEXT,
            hostname TEXT,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            custom_name TEXT,
            is_favorite INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Internationalisation (i18n) ---
translations = {
    'en': {
        'wol_sent': 'WOL packet sent to {}', 'wol_error': 'Error sending WOL packet: {}',
        'device_online': 'Device is online.', 'device_offline': 'Device is offline.',
        'ping_error': 'Error during ping: {}', 'scan_started': 'Network scan started on {}...',
        'scan_error': 'Error during network scan: {}', 'scan_finished': 'Scan finished. Found {} devices.'
    },
    'fr': {
        'wol_sent': 'Paquet WOL envoyé à {}', 'wol_error': 'Erreur lors de l\'envoi du paquet WOL : {}',
        'device_online': 'L\'appareil est en ligne.', 'device_offline': 'L\'appareil est hors ligne.',
        'ping_error': 'Erreur durant le ping : {}', 'scan_started': 'Scan réseau démarré sur {}...',
        'scan_error': 'Erreur durant le scan réseau : {}', 'scan_finished': 'Scan terminé. {} appareils trouvés.'
    },
    'es': {
        'wol_sent': 'Paquete WOL enviado a {}', 'wol_error': 'Error al enviar el paquete WOL: {}',
        'device_online': 'El dispositivo está en línea.', 'device_offline': 'El dispositivo está fuera de línea.',
        'ping_error': 'Error durante el ping: {}', 'scan_started': 'Escaneo de red iniciado en {}...',
        'scan_error': 'Error durante el escaneo de red: {}', 'scan_finished': 'Escaneo finalizado. Se encontraron {} dispositivos.'
    },
    'de': {
        'wol_sent': 'WOL-Paket an {} gesendet', 'wol_error': 'Fehler beim Senden des WOL-Pakets: {}',
        'device_online': 'Gerät ist online.', 'device_offline': 'Gerät ist offline.',
        'ping_error': 'Fehler beim Ping: {}', 'scan_started': 'Netzwerk-Scan auf {} gestartet...',
        'scan_error': 'Fehler beim Netzwerk-Scan: {}', 'scan_finished': 'Scan beendet. {} Geräte gefunden.'
    }
}

def get_lang(request):
    lang = request.headers.get('Accept-Language', 'en').split(',')[0].split('-')[0]
    return lang if lang in translations else 'en'

def _(lang, key, *args):
    return translations[lang].get(key, key).format(*args)

# --- Logique Métier ---
def get_network_range():
    try:
        iface = conf.iface
        ip_addr = get_if_addr(iface)
        net_mask = get_if_net(iface)
        return f"{ip_addr}/{net_mask.split('/')[1]}"
    except Exception:
        return "192.168.1.0/24"

def network_scanner():
    while True:
        target_ip_range = get_network_range()
        print(_('en', 'scan_started', target_ip_range))
        try:
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip_range)
            result = srp(arp_request, timeout=5, verbose=False)[0]
            devices = [{'ip': r.psrc, 'mac': r.hwsrc} for s, r in result]
            conn = get_db_connection()
            cursor = conn.cursor()
            for device in devices:
                cursor.execute(
                    "INSERT INTO devices (mac, ip, last_seen) VALUES (?, ?, CURRENT_TIMESTAMP) "
                    "ON CONFLICT(mac) DO UPDATE SET ip=excluded.ip, last_seen=CURRENT_TIMESTAMP",
                    (device['mac'], device['ip'])
                )
            cursor.execute("DELETE FROM devices WHERE last_seen < datetime('now', ?)", ('-' + str(DEVICE_EXPIRATION_DAYS) + ' days',))
            conn.commit()
            conn.close()
            print(_('en', 'scan_finished', len(devices)))
        except Exception as e:
            print(_('en', 'scan_error', str(e)))
        time.sleep(SCAN_INTERVAL_SECONDS)

def send_wol_packet(mac_address):
    mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, ('<broadcast>', 9))

def ping_with_scapy(ip):
    try:
        ans = sr1(IP(dst=ip)/ICMP(), timeout=1, verbose=0)
        return ans is not None
    except Exception:
        return False

# --- Endpoints API ---
@app.route('/')
def root():
    return send_from_directory('ui', 'index.html')

@app.route('/assets/<path:path>')
def send_asset(path):
    return send_from_directory('assets', path)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    conn = get_db_connection()
    devices = conn.execute('SELECT * FROM devices ORDER BY last_seen DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in devices])

@app.route('/api/wol/<mac>', methods=['POST'])
def wake_device(mac):
    lang = get_lang(request)
    try:
        send_wol_packet(mac)
        return jsonify({'status': 'success', 'message': _(lang, 'wol_sent', mac)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': _(lang, 'wol_error', str(e))}), 500

@app.route('/api/ping/<ip>', methods=['GET'])
def ping_device(ip):
    lang = get_lang(request)
    if ping_with_scapy(ip):
        return jsonify({'status': 'online', 'message': _(lang, 'device_online')})
    else:
        return jsonify({'status': 'offline', 'message': _(lang, 'device_offline')})

# --- Exécution ---
if __name__ == '__main__':
    # Pour test local uniquement
    print("Initializing Coyote WOL Tool for local testing...")
    init_db()
    scanner_thread = threading.Thread(target=network_scanner, daemon=True)
    scanner_thread.start()
    app.run(host='0.0.0.0', port=5001, debug=True)
else:
    # Pour production (lancé par Gunicorn sur le NAS)
    init_db()
    scanner_thread = threading.Thread(target=network_scanner, daemon=True)
    scanner_thread.start()
