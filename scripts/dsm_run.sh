#!/bin/sh
# Rôle : Démarre le serveur web Gunicorn lorsque le paquet est lancé.

PACKAGE_DIR="/var/packages/coyotewol/target"
# Utilise le chemin relatif vers Gunicorn qui est inclus dans le paquet
GUNICORN_EXECUTABLE="${PACKAGE_DIR}/vendor/gunicorn/app/wsgiapp.py"
PYTHON_EXECUTABLE="/usr/local/bin/python3"
PID_FILE="${PACKAGE_DIR}/gunicorn.pid"
LOG_FILE="${PACKAGE_DIR}/coyote_wol.log"

cd ${PACKAGE_DIR}

${PYTHON_EXECUTABLE} ${GUNICORN_EXECUTABLE} \
    --workers 1 \
    --bind 0.0.0.0:5001 \
    --pid ${PID_FILE} \
    --log-level info \
    --log-file ${LOG_FILE} \
    --daemon \
    main:app
