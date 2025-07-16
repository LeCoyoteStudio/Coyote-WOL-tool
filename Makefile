SPK_NAME = CoyoteWOLtool
SPK_VERS = 2.1.0
SPK_REV = 1
SPK_ICON = images/CoyoteWOLtool-72.png

MAINTAINER = Coyote Studio
DESCRIPTION = From a Synology NAS - Scans the network and allows remote waking of devices via Wake-on-LAN.
STARTABLE = yes
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Passage du projet sous licence MIT."

HOMEPAGE = https://coyote.studio
LICENSE = MIT

# Inclusion des règles de compilation de spksrc
include ../../mk/spksrc.spk.mk

