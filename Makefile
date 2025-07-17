# Makefile pour le paquet Synology CoyoteWOLtool
# Ce fichier définit les variables et les règles nécessaires pour la compilation.

# --- Variables de base du paquet ---
SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.7
SPK_REV = 2 # Incrémentation de la révision pour ce correctif
SPK_ICON = images/CoyoteWOLtool-72.png

# --- Métadonnées du paquet ---
MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Correction de la structure des répertoires pour la compilation."

# --- Liens et licence ---
HOMEPAGE = https://coyote.studio
LICENSE = MIT

# --- Cible d'installation ---
# C'est la règle la plus importante. Elle est exécutée par spksrc pour copier
# les fichiers de votre projet dans le répertoire de travail final avant la mise en paquet.
# '$(INSTALL_DIR)' est une variable fournie par spksrc qui pointe vers le bon dossier de destination.
install_target:
	@echo "Copying application source files to installation directory..."
	# Crée le répertoire 'target' dans la destination d'installation.
	@mkdir -p $(INSTALL_DIR)/target
	# Copie l'intégralité du dossier 'src' dans le dossier 'target'.
	# Cela créera la structure /target/src/ qui est attendue par les scripts.
	@cp -a src $(INSTALL_DIR)/target/

# --- Inclusion des règles de compilation standards ---
# Cette ligne est cruciale. Elle importe toutes les règles de compilation standards
# de spksrc, ce qui automatise la majeure partie du processus de construction du .spk.
include ../../mk/spksrc.spk.mk
