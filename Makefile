SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.6
SPK_REV = 1
SPK_ICON = images/CoyoteWOLtool-72.png

MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Simplification de la règle d'installation dans le Makefile."

HOMEPAGE = https://coyote.studio
LICENSE = MIT

# Règle d'installation pour copier les fichiers de l'application dans le dossier de préparation.
# Le système de build se chargera de créer la structure finale du paquet.
install_target:
	@mkdir -p $(STAGING_DIR)
	@cp -a src/* $(STAGING_DIR)/

# Inclusion des règles de compilation de spksrc
include ../../mk/spksrc.spk.mk
