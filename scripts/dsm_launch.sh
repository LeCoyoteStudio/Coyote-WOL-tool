#!/bin/sh

# ==============================================================================
# Script de contrôle (Démarrer/Arrêter/Statut) pour CoyoteWOLtool
# ==============================================================================

# --- Variables de configuration ---
PACKAGE_NAME="CoyoteWOLtool"
# CORRECTION : Le chemin pointe maintenant directement vers le dossier du paquet.
PACKAGE_DIR="/var/packages/${PACKAGE_NAME}"
PYTHON_BIN="/usr/bin/python3"
API_SCRIPT="${PACKAGE_DIR}/src/main.py"
PID_FILE="${PACKAGE_DIR}/var/${PACKAGE_NAME}.pid"
LOG_FILE="/var/log/${PACKAGE_NAME}.log"
RUN_AS_USER="sc-${PACKAGE_NAME}"

# --- Fonctions de contrôle ---

start_daemon() {
    echo "Attempting to start ${PACKAGE_NAME} API server..." >> ${LOG_FILE}
    start-stop-daemon --start --quiet --background \
        --chuid ${RUN_AS_USER} \
        --exec ${PYTHON_BIN} -- ${API_SCRIPT} \
        --make-pidfile --pidfile ${PID_FILE}
    
    sleep 2
    if [ -f ${PID_FILE} ] && ps -p $(cat ${PID_FILE}) > /dev/null; then
        echo "Server started successfully with PID $(cat ${PID_FILE})." >> ${LOG_FILE}
    else
        echo "ERROR: Failed to start the server. Check logs for details." >> ${LOG_FILE}
        rm -f ${PID_FILE}
        exit 1
    fi
}

stop_daemon() {
    echo "Attempting to stop ${PACKAGE_NAME} API server..." >> ${LOG_FILE}
    start-stop-daemon --stop --quiet --pidfile ${PID_FILE} --retry 5
    
    if [ ! -f ${PID_FILE} ]; then
        echo "Server stopped successfully." >> ${LOG_FILE}
    else
        echo "Warning: Server may not have stopped correctly." >> ${LOG_FILE}
    fi
}

daemon_status() {
    if [ -f ${PID_FILE} ]; then
        PID=$(cat ${PID_FILE})
        if ps -p ${PID} > /dev/null; then
            echo "${PACKAGE_NAME} is running with PID: ${PID}"
            exit 0
        else
            echo "${PACKAGE_NAME} is not running, but a stale PID file exists. Cleaning up."
            rm -f ${PID_FILE}
            exit 1
        fi
    else
        echo "${PACKAGE_NAME} is not running."
        exit 3
    fi
}

# --- Logique principale du script ---
case $1 in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    status)
        daemon_status
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac

exit 0
