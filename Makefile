SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.3
SPK_REV = 1
SPK_ICON = images/CoyoteWOLtool-72.png

MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Retour à un Makefile basique pour le diagnostic."

HOMEPAGE = https://coyote.studio
LICENSE = MIT

# Inclusion des règles de compilation de spksrc
# Le système de build standard se chargera de la copie des fichiers.
include ../../mk/spksrc.spk.mk
