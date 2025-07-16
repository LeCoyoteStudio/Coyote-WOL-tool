from flask import Flask, jsonify, request, render_template, url_for
import sqlite3
import datetime
import socket
import os
import re
import subprocess

# --- Configuration ---
PACKAGE_NAME = "CoyoteWOLtool"
DB_FILE = f"/var/packages/{PACKAGE_NAME}/var/devices.db"
APP_PORT = 9989

app = Flask(__name__, template_folder='templates', static_folder='static')

# --- Internationalisation (i18n) ---
translations = {
    'en': { 'invalid_mac': "Invalid MAC address format", 'packet_sent': "Magic packet sent to {mac}", 'generic_error': "An error occurred: {error}", 'invalid_ip': "Invalid IP address format" },
    'fr': { 'invalid_mac': "Format d'adresse MAC invalide", 'packet_sent': "Paquet magique envoyé à {mac}", 'generic_error': "Une erreur est survenue : {error}", 'invalid_ip': "Format d'adresse IP invalide" },
    'es': { 'invalid_mac': "Formato de dirección MAC no válido", 'packet_sent': "Paquete mágico enviado a {mac}", 'generic_error': "Ocurrió un error: {error}", 'invalid_ip': "Formato de dirección IP no válido" },
    'de': { 'invalid_mac': "Ungültiges MAC-Adressformat", 'packet_sent': "Magic Packet an {mac} gesendet", 'generic_error': "Ein Fehler ist aufgetreten: {error}", 'invalid_ip': "Ungültiges IP-Adressformat" }
}

def get_locale():
    lang_arg = request.args.get('lang')
    if lang_arg and lang_arg in translations:
        return lang_arg
    languages = request.headers.get('Accept-Language')
    if not languages:
        return 'en'
    for lang in languages.replace(' ', '').split(','):
        lang_code = lang.split(';')[0].split('-')[0].lower()
        if lang_code in translations:
            return lang_code
    return 'en'

def _(key, **kwargs):
    locale = get_locale()
    return translations.get(locale, translations['en']).get(key, key).format(**kwargs)

# --- Fonctions utilitaires ---
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def send_wol_packet(mac_address: str):
    mac_address = mac_address.replace(':', '').replace('-', '').upper()
    if len(mac_address) != 12 or not all(c in '0123456789ABCDEF' for c in mac_address):
        raise ValueError(_('invalid_mac'))
    magic_packet = b'\xff' * 6 + (bytes.fromhex(mac_address) * 16)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(magic_packet, ('255.255.255.255', 9))

# --- Route pour l'interface Web ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Endpoints de l'API ---
@app.route('/api/languages', methods=['GET'])
def get_available_languages():
    return jsonify(list(translations.keys()))

@app.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        conn = get_db_connection()
        ninety_days_ago = datetime.datetime.now() - datetime.timedelta(days=90)
        devices = conn.execute(
            '''SELECT mac, ip, hostname, last_seen, custom_name, is_favorite 
               FROM devices WHERE last_seen >= ? ORDER BY is_favorite DESC, last_seen DESC''',
            (ninety_days_ago,)
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in devices])
    except Exception as e:
        return jsonify({"error": _('generic_error', error=str(e))}), 500

@app.route('/api/ping/<ip_address>', methods=['GET'])
def ping_device(ip_address):
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip_address):
        return jsonify({"status": "error", "message": _('invalid_ip')}), 400
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip_address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return jsonify({"status": "online" if result.returncode == 0 else "offline"})
    except Exception as e:
        return jsonify({"status": "error", "message": _('generic_error', error=str(e))}), 500

@app.route('/api/wakeup', methods=['POST'])
def wakeup_device():
    mac = request.get_json().get('mac')
    try:
        send_wol_packet(mac)
        return jsonify({"status": "success", "message": _('packet_sent', mac=mac)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Lancement du serveur ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT, debug=False)
