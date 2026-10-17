APP_ID := io.github.phni.Pomodoro98
MANIFEST := $(APP_ID).yml
BUILD_DIR := build-dir
BUILDER_APP := org.flatpak.Builder
RUNTIME_VERSION := 25.08
FLATPAK_BUILDER := flatpak run --command=flatpak-builder $(BUILDER_APP) --disable-rofiles-fuse
FLATPAK_LINTER := flatpak run --command=flatpak-builder-lint $(BUILDER_APP)

.PHONY: help check-flatpak setup-flatpak build rebuild lint test \
	run run-flatpak install uninstall clean

help:
	@echo "Pomodoro98 development commands"
	@echo ""
	@echo "  make setup-flatpak  Install Builder and Freedesktop 25.08 prerequisites"
	@echo "  make build          Build using Flatpak Builder's module cache"
	@echo "  make rebuild        Rebuild all modules without the module cache"
	@echo "  make lint           Validate Python, shell, desktop, AppStream, and manifest"
	@echo "  make test           Run non-interactive checks against the Flatpak build"
	@echo "  make run            Run the app directly from the source tree"
	@echo "  make install        Build and install the Flatpak for the current user"
	@echo "  make run-flatpak    Run the installed Flatpak"
	@echo "  make uninstall      Remove the user-local Flatpak and debug extension"
	@echo "  make clean          Remove ignored local Flatpak build output"

check-flatpak:
	@command -v flatpak >/dev/null || { \
		echo "Flatpak is not installed. Install it with your system package manager." >&2; \
		exit 1; \
	}
	@flatpak remotes --columns=name | grep -Fxq flathub || { \
		echo "The Flathub remote is missing. See https://flathub.org/setup" >&2; \
		exit 1; \
	}

setup-flatpak: check-flatpak
	flatpak install -y flathub $(BUILDER_APP)
	flatpak install -y flathub \
		org.freedesktop.Platform//$(RUNTIME_VERSION) \
		org.freedesktop.Sdk//$(RUNTIME_VERSION)

build: check-flatpak
	$(FLATPAK_BUILDER) --force-clean $(BUILD_DIR) $(MANIFEST)

rebuild: check-flatpak
	$(FLATPAK_BUILDER) --disable-cache --force-clean $(BUILD_DIR) $(MANIFEST)

lint: check-flatpak
	python3 -m compileall -q src
	desktop-file-validate flatpak/$(APP_ID).desktop
	appstreamcli validate --no-net --strict flatpak/$(APP_ID).metainfo.xml
	$(FLATPAK_LINTER) manifest $(MANIFEST)

test: build
	flatpak build $(BUILD_DIR) \
		python3 -c 'import tkinter; print("Tkinter import passed", tkinter.TclVersion, tkinter.TkVersion)'
	flatpak build $(BUILD_DIR) \
		python3 -c 'import pomodoro98, pomodoro98.app, pomodoro98.sound as s, pomodoro98.tray as t; assert not t.TRAY_OK; assert s._SA is None; assert s._PYG is None; import pomodoro98.app as a; assert a.SOUND_FOCUS_END.exists() and a.ICON_FOCUS_FILE.exists(); print("Fallback import passed", pomodoro98.__version__)'
	flatpak build $(BUILD_DIR) test -x /app/bin/pomodoro98

run:
	PYTHONPATH=src python3 -m pomodoro98

install: check-flatpak
	$(FLATPAK_BUILDER) --user --install --force-clean $(BUILD_DIR) $(MANIFEST)

run-flatpak:
	flatpak run $(APP_ID)

uninstall:
	-flatpak uninstall --user -y $(APP_ID)
	-flatpak uninstall --user -y $(APP_ID).Debug

clean:
	flatpak run --command=sh $(BUILDER_APP) -c \
		'rm -rf /run/host/$(CURDIR)/$(BUILD_DIR) /run/host/$(CURDIR)/.flatpak-builder'
