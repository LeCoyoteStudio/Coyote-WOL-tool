# Makefile pour le paquet Synology CoyoteWOLtool
# Ce fichier définit les variables et les règles nécessaires pour la compilation.

# --- Variables de base du paquet ---
SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.7
SPK_REV = 4 # Incrémentation de la révision pour ce correctif majeur.
SPK_ICON = images/CoyoteWOLtool-72.png

# --- Métadonnées du paquet ---
MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Correction majeure : copie de tous les fichiers requis dans le paquet et simplification de la structure des répertoires."

# --- Liens et licence ---
HOMEPAGE = https://coyote.studio
LICENSE = MIT

# --- Cible d'installation ---
# C'est la règle la plus importante. Elle est exécutée par spksrc pour copier
# les fichiers de votre projet dans le répertoire de travail final avant la mise en paquet.
install_target:
	@echo "Copying all package files to installation directory..."
	# Crée le répertoire d'installation s'il n'existe pas.
	@mkdir -p $(INSTALL_DIR)
	# Copie tous les dossiers nécessaires directement à la racine du paquet.
	@cp -a src $(INSTALL_DIR)/
	@cp -a scripts $(INSTALL_DIR)/
	@cp -a conf $(INSTALL_DIR)/
	@cp -a images $(INSTALL_DIR)/

# --- Inclusion des règles de compilation standards ---
# Cette ligne est cruciale. Elle importe toutes les règles de compilation standards
# de spksrc, ce qui automatise la majeure partie du processus de construction du .spk.
include ../../mk/spksrc.spk.mk
