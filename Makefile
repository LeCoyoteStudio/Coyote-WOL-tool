SPK_NAME = CoyoteWOLtool
SPK_VERS = 1.0.0
SPK_REV  = 1
SPK_ICON = src/ui/static/Icon.png

MAINTAINER = Coyote Studio
DESCRIPTION = Wake-on-LAN utility for Synology DSM
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = Initial release

HOMEPAGE = https://github.com/LeCoyoteStudio/Coyote-WOL-tool
LICENSE  = MIT

STARTABLE = no

include ../../mk/spksrc.spk.mk

# ----------------------------------------------------------
# MUST exist – tells spksrc how to fill the staging directory
install_target:
	@install -vd $(STAGING_INSTALL_PREFIX)/bin
	@install -v  -m755 src/coyote-wol-backend $(STAGING_INSTALL_PREFIX)/bin/

	@install -vd $(STAGING_INSTALL_PREFIX)/ui
	@cp -vr src/ui/* $(STAGING_INSTALL_PREFIX)/ui/
