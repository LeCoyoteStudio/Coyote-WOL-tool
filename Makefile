SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.1
SPK_REV = 1
SPK_ICON = images/CoyoteWOLtool-72.png

MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Suppression de la règle d'installation personnalisée pour utiliser le processus de build par défaut."

HOMEPAGE = https://coyote.studio
LICENSE = MIT

# Inclusion des règles de compilation de spksrc
# Le système de build standard se chargera de la copie des fichiers.
include ../../mk/spksrc.spk.mk
