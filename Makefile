# Makefile pour le paquet Synology CoyoteWOLtool
# Ce fichier définit les variables et les règles nécessaires pour la compilation.

# --- Variables de base du paquet ---
# Nom du paquet (doit correspondre au nom du dossier dans spk/ et au fichier INFO)
SPK_NAME = CoyoteWOLtool
# Version du paquet. Doit être synchronisée avec le fichier INFO.
SPK_VERS = 0.1.7
# Numéro de révision. Incrémenter pour des changements de packaging sans changer la version du logiciel.
SPK_REV = 1
# Chemin vers l'icône principale du paquet.
SPK_ICON = images/CoyoteWOLtool-72.png

# --- Métadonnées du paquet (redondant avec INFO mais utilisé par spksrc) ---
MAINTAINER = Coyote Studio
DESCRIPTION = Scanne le réseau et permet de réveiller à distance les appareils via Wake-on-LAN.
# Indique si le paquet peut être démarré/arrêté depuis le Centre de Paquets.
STARTABLE = yes
# Nom affiché dans l'interface de spksrc.
DISPLAY_NAME = Coyote WOL tool
# Journal des modifications pour cette version du paquet.
CHANGELOG = "Amélioration et standardisation du Makefile et des scripts."

# --- Liens et licence ---
HOMEPAGE = https://coyote.studio
LICENSE = MIT

# --- Cible d'installation ---
# C'est la règle la plus importante. Elle est exécutée par spksrc pour copier
# les fichiers de votre projet dans le répertoire de travail final avant la mise en paquet.
# '$(INSTALL_DIR)' est une variable fournie par spksrc qui pointe vers le bon dossier de destination.
# '$(WORK_DIR)' est le répertoire où se trouvent les sources de votre projet.
install_target:
	@echo "Copying application source files to installation directory..."
	# Crée le répertoire 'target' dans la destination d'installation.
	@mkdir -p $(INSTALL_DIR)/target
	# Copie tout le contenu du dossier 'src' de notre projet vers le dossier 'target' de destination.
	@cp -a $(WORK_DIR)/src/* $(INSTALL_DIR)/target/

# --- Inclusion des règles de compilation standards ---
# Cette ligne est cruciale. Elle importe toutes les règles de compilation standards
# de spksrc, ce qui automatise la majeure partie du processus de construction du .spk.
include ../../mk/spksrc.spk.mk
