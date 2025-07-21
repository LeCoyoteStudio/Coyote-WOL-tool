SPK_NAME = CoyoteWOLtool
SPK_VERS = 1.0.0
SPK_REV  = 1
SPK_ICON = src/ui/static/icon.png   # lowercase is fine

MAINTAINER = Coyote Studio
DESCRIPTION = Wake-on-LAN utility for Synology DSM
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = Initial release

HOMEPAGE = https://github.com/LeCoyoteStudio/Coyote-WOL-tool
LICENSE  = MIT

STARTABLE = no

# ----------------------------------------------------------
# This rule **must** exist – otherwise staging stays empty
include ../../mk/spksrc.spk.mk

.PHONY: coyote_install
coyote_install:
	@install -vd $(STAGING_INSTALL_PREFIX)/bin
	@install -v  -m755 src/coyote-wol-backend $(STAGING_INSTALL_PREFIX)/bin/

	@install -vd $(STAGING_INSTALL_PREFIX)/ui
	@cp -vr src/ui/* $(STAGING_INSTALL_PREFIX)/ui/

install_target: coyote_install
