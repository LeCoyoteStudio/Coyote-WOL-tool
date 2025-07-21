SPK_NAME = CoyoteWOLtool
SPK_VERS = 1.0.0
SPK_REV  = 1
SPK_ICON = src/ui/static/Icon.png

DEPENDS =
MAINTAINER = Coyote Studio
DESCRIPTION = Wake-on-LAN utility for Synology DSM
DISPLAY_NAME = Coyote WOL tool
CHANGELOG  = "Initial release"

HOMEPAGE = https://github.com/LeCoyoteStudio/Coyote-WOL-tool
LICENSE  = MIT

STARTABLE = no
SERVICE_SETUP = src/service-setup.sh   # remove if you don’t have this file

# -------------------------------------------------------------
include ../../mk/spksrc.spk.mk

# ---- 100 % traced install ----------------------------------
.PHONY: coyote_install
coyote_install:
	@echo "=== DBG: starting install ================================="
	@set -x
	@ls -la src/ || echo "src/ does not exist"
	@ls -la src/ui/ || echo "src/ui/ does not exist"
	@ls -la src/coyote-wol-backend || echo "backend binary missing"

	@install -v -d $(STAGING_INSTALL_PREFIX)/bin
	@install -v -m 755 src/coyote-wol-backend $(STAGING_INSTALL_PREFIX)/bin/

	@install -v -d $(STAGING_INSTALL_PREFIX)/ui
	@cp -vr src/ui/* $(STAGING_INSTALL_PREFIX)/ui/

	@echo "=== DBG: install finished ================================="
	@set +x

# hook into spksrc
install_target: coyote_install
