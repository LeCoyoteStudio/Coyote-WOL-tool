SPK_NAME = CoyoteWOLtool
SPK_VERS = 1.0.0
SPK_REV = 1
SPK_ICON = src/ui/static/Icon.png

DEPENDS =

MAINTAINER = Coyote Studio
DESCRIPTION = Wake-on-LAN tool for Synology DSM
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = "Initial release"

HOMEPAGE = https://github.com/LeCoyoteStudio/Coyote-WOL-tool
LICENSE  = MIT

STARTABLE = no
SERVICE_SETUP = src/service-setup.sh

SPK_DEPENDS = "Python3>=3.8"

include ../../mk/spksrc.spk.mk
