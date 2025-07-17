# Makefile pour le paquet Synology CoyoteWOLtool
# Ce fichier définit les variables et les règles nécessaires pour la compilation.

# --- Variables de base du paquet ---
SPK_NAME = CoyoteWOLtool
SPK_VERS = 0.1.7
SPK_REV = 8 # Incrémentation de la révision pour le correctif de syntaxe.
SPK_ICON = images/CoyoteWOLtool-72.png

# --- Métadonnées du paquet ---
MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Correction de la syntaxe du Makefile (remplacement des espaces par des tabulations)."

# --- Liens et licence ---
HOMEPAGE = https://coyote.studio
LICENSE = MIT

# --- Cible d'installation ---
# C'est la règle la plus importante. spksrc l'exécute pour copier les fichiers
# de votre projet dans le répertoire de travail final avant la mise en paquet.
# IMPORTANT : Les lignes de commande ci-dessous DOIVENT être indentées avec une tabulation, pas des espaces.
install_target:
	@echo "Copying all package files to installation directory..."
	@mkdir -p $(INSTALL_DIR)
	@cp -a src $(INSTALL_DIR)/
	@cp -a scripts $(INSTALL_DIR)/
	@cp -a conf $(INSTALL_DIR)/
	@cp -a images $(INSTALL_DIR)/

# --- Inclusion des règles de compilation standards ---
# Cette ligne est cruciale. Elle importe toutes les règles de compilation standards
# de spksrc, ce qui automatise la majeure partie du processus de construction du .spk.
include ../../mk/spksrc.spk.mk
