SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.2.0
SPK_REV = 1
SPK_ICON = images/CoyoteWOLtool-72.png

MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Correction du Makefile pour utiliser les règles de compilation Python (spksrc.python-module.mk)."

HOMEPAGE = https://coyote.studio
LICENSE = MIT

# Inclusion des règles de compilation spécifiques aux modules Python
# C'est cette ligne qui résout le problème de création du paquet.
include ../../mk/spksrc.python-module.mk
