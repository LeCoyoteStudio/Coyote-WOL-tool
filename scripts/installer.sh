#!/bin/sh
# Rôle : Exécuté une seule fois lors de l'installation du paquet sur le NAS.

echo "Coyote WOL Tool installation script."
# Les dépendances sont incluses, aucune installation n'est nécessaire.
# On s'assure juste que les scripts de gestion sont exécutables.
chmod +x /var/packages/coyotewol/target/dsm_*.sh
exit 0
