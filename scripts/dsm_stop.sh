#!/bin/sh

# ==============================================================================
# Script de post-désinstallation pour CoyoteWOLtool
#
# Ce script est exécuté par le système DSM juste avant la suppression
# complète des fichiers du paquet.
# Son unique rôle est de nettoyer les configurations ajoutées au système,
# principalement la tâche planifiée.
# ==============================================================================

# --- Variables de configuration ---
PACKAGE_NAME="CoyoteWOLtool"
# Nom de la tâche planifiée à supprimer.
TASK_NAME="${PACKAGE_NAME}_Scan"
# Fichier de log pour le suivi de la désinstallation.
LOG_FILE="/var/log/${PACKAGE_NAME}_uninstall.log"

# --- Début du script ---

# Redirige toute la sortie vers le fichier de log.
exec > ${LOG_FILE} 2>&1

echo "====================================================="
echo "Starting ${PACKAGE_NAME} post-uninstallation script"
echo "Date: $(date)"
echo "====================================================="

# Étape 1: Suppression de la tâche planifiée
echo "[STEP 1/1] Deleting scheduled task '${TASK_NAME}'..."

# La commande 'synoschedtask --del' supprime la tâche portant le nom donné.
# On vérifie si la commande a réussi.
if /usr/syno/bin/synoschedtask --del name="${TASK_NAME}"; then
    echo "Scheduled task '${TASK_NAME}' deleted successfully."
else
    # Cette erreur peut se produire si la tâche n'existait pas, ce qui n'est pas critique.
    echo "Warning: Could not delete scheduled task '${TASK_NAME}'. It might have been already removed."
fi

echo "====================================================="
echo "Post-uninstallation script finished."
echo "====================================================="

# Le script doit toujours se terminer avec un code de sortie 0.
exit 0
