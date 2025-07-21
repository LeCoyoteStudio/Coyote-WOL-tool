SPK_NAME = CoyoteWOLtool
SPK_VERS = 1.0.0
SPK_REV  = 1
SPK_ICON = src/ui/static/Icon.png

DEPENDS =

MAINTAINER = Coyote Studio
DESCRIPTION = Wake-on-LAN utility for Synology DSM
DISPLAY_NAME = Coyote WOL tool
CHANGELOG = Initial release

HOMEPAGE = https://github.com/LeCoyoteStudio/Coyote-WOL-tool
LICENSE  = MIT

STARTABLE = no

include ../../mk/spksrc.spk.mk

.PHONY: coyote_install
coyote_install:
	@install -d $(STAGING_INSTALL_PREFIX)/bin
	@install -m 755 src/coyote-wol-backend $(STAGING_INSTALL_PREFIX)/bin/

	@install -d $(STAGING_INSTALL_PREFIX)/ui
	@cp -r src/ui/* $(STAGING_INSTALL_PREFIX)/ui/

install_target: coyote_install
