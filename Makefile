SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.0
SPK_REV = 1
SPK_ICON = images/CoyoteWOLtool-72.png

MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Ajout d'une règle d'installation explicite dans le Makefile pour corriger la compilation."

HOMEPAGE = https://coyote.studio
LICENSE = MIT

# Règle d'installation personnalisée pour copier les fichiers du projet au bon endroit
install_target:
	@mkdir -p $(STAGING_DIR)/src
	@cp -a src/* $(STAGING_DIR)/src/
	@mkdir -p $(STAGING_DIR)/conf
	@cp -a conf/* $(STAGING_DIR)/conf/
	@mkdir -p $(STAGING_DIR)/scripts
	@cp -a scripts/* $(STAGING_DIR)/scripts/

# Inclusion des règles de compilation de spksrc
include ../../mk/spksrc.spk.mk
