SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.5
SPK_REV = 1
SPK_ICON = images/CoyoteWOLtool-72.png

MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Ajout du logging de la variable STAGING_DIR pour le débogage."

HOMEPAGE = https://coyote.studio
LICENSE = MIT

# Règle d'installation pour copier les fichiers de l'application dans le dossier 'target'
# qui sera déployé sur le NAS. Le reste (conf, scripts) est géré automatiquement.
install_target:
	@echo "STAGING_DIR is: $(STAGING_DIR)"
	@mkdir -p $(STAGING_DIR)/target
	@cp -a src/* $(STAGING_DIR)/target/

# Inclusion des règles de compilation de spksrc
include ../../mk/spksrc.spk.mk
