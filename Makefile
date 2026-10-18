APP_ID := io.github.phni.Pomodoro98
MANIFEST := $(APP_ID).yml
BUILD_DIR := build-dir
REPO_DIR := repo
LOCAL_REMOTE := pomodoro98-local
BUILDER_APP := org.flatpak.Builder
RUNTIME_VERSION := 25.08
FLATPAK_BUILDER := flatpak run --command=flatpak-builder $(BUILDER_APP) --disable-rofiles-fuse
FLATPAK_LINTER := flatpak run --command=flatpak-builder-lint $(BUILDER_APP)

.PHONY: help check-flatpak setup-flatpak build rebuild lint lint-py lint-flatpak format test test-py \
	run run-flatpak install uninstall clean

help:
	@echo "Pomodoro98 development commands"
	@echo ""
	@echo "  make setup-flatpak  Install Builder and Freedesktop 25.08 prerequisites"
	@echo "  make build          Build using Flatpak Builder's module cache"
	@echo "  make rebuild        Rebuild all modules without the module cache"
	@echo "  make lint           Run lint-py and lint-flatpak"
	@echo "  make lint-py        Ruff, syntax, and version checks (no Flatpak needed)"
	@echo "  make lint-flatpak   Validate desktop file, AppStream, and manifest"
	@echo "  make format         Format Python code with ruff"
	@echo "  make test-py        Run the pytest suite with coverage"
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

lint: lint-py lint-flatpak

lint-py:
	python3 -m compileall -q src scripts
	ruff check src scripts tests
	ruff format --check src scripts tests
	python3 scripts/check_version.py

lint-flatpak: check-flatpak
	desktop-file-validate flatpak/$(APP_ID).desktop
	appstreamcli validate --no-net --strict flatpak/$(APP_ID).metainfo.xml
	$(FLATPAK_LINTER) manifest $(MANIFEST)

test-py:
	python3 -m pytest --cov=pomodoro98 --cov-report=term-missing

test: build
	flatpak build $(BUILD_DIR) \
		python3 -c 'import tkinter; print("Tkinter import passed", tkinter.TclVersion, tkinter.TkVersion)'
	flatpak build $(BUILD_DIR) \
		python3 -c 'import pomodoro98, pomodoro98.app, pomodoro98.sound as s, pomodoro98.tray as t; assert not t.TRAY_OK; assert s._SA is None; assert s._PYG is None; import pomodoro98.app as a; assert a.SOUND_FOCUS_END.exists() and a.ICON_FOCUS_FILE.exists(); print("Fallback import passed", pomodoro98.__version__)'
	flatpak build $(BUILD_DIR) test -x /app/bin/pomodoro98

format:
	ruff format src scripts tests
	ruff check --fix src scripts tests

run:
	PYTHONPATH=src python3 -m pomodoro98

# Build into a local repo with Builder, then install with the host's flatpak.
# Installing from inside the Builder sandbox would export a desktop file whose
# Exec is the sandbox path /app/bin/flatpak, which hides the app from launchers.
install: check-flatpak
	$(FLATPAK_BUILDER) --force-clean --repo=$(REPO_DIR) $(BUILD_DIR) $(MANIFEST)
	flatpak remote-add --user --if-not-exists --no-gpg-verify \
		$(LOCAL_REMOTE) $(CURDIR)/$(REPO_DIR)
	flatpak install --user -y --reinstall $(LOCAL_REMOTE) $(APP_ID)

run-flatpak:
	flatpak run $(APP_ID)

uninstall:
	-flatpak uninstall --user -y $(APP_ID)
	-flatpak uninstall --user -y $(APP_ID).Debug
	-flatpak remote-delete --user $(LOCAL_REMOTE)

clean:
	flatpak run --command=sh $(BUILDER_APP) -c \
		'rm -rf $(CURDIR)/$(BUILD_DIR) $(CURDIR)/$(REPO_DIR) $(CURDIR)/.flatpak-builder'
