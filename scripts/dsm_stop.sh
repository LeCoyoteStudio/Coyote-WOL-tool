#!/bin/sh
# Rôle : Arrête proprement le serveur web lorsque le paquet est stoppé.

PACKAGE_DIR="/var/packages/coyotewol/target"
PID_FILE="${PACKAGE_DIR}/gunicorn.pid"

if [ -f ${PID_FILE} ]; then
    kill $(cat ${PID_FILE})
    rm -f ${PID_FILE}
fi
