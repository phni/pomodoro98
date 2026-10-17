# Pomodoro98 Flatpak Publication TODO

## 1. Project Readiness

- [x] Fix local source launch when Tkinter is missing.
  - [x] Confirm the system Python lacks Tkinter and document the Ubuntu prerequisite.
  - [x] Install `python3-tk` using interactive sudo in the user's terminal; automated installation requires authentication. (`python3-tk` 3.14.3)
  - [x] Verify `make run` opens the application after installation.

- [x] Choose the canonical entry point (`pomodoro98.py` or `pomodoro98_2.py`) and remove or clearly document the other variant. (`pomodoro98_2.py`)
- [x] Add an open-source `LICENSE`; record its SPDX identifier for AppStream metadata. (`MIT`)
- [x] Complete `README.md` with run instructions, supported Linux desktops, screenshots, and maintainer contact details.
- [x] Add versioning and create a tagged source release; Flathub expects a meaningful development history and standard releases. (`v0.1.0`)
- [x] Make asset paths independent of the current working directory (resolve them relative to the installed application).
- [x] Confirm focus/rest sound filenames match the files actually shipped. (`focus_end.wav`, `reset_end.wav`)

## 2. Flatpak Identity and Desktop Integration

- [x] Select a permanent reverse-DNS application ID. Prefer `io.github.<owner>.Pomodoro98` if this repository will be hosted on GitHub; confirm the owner and repository URL first. (`io.github.phni.Pomodoro98`)
- [x] Rename exported files to match the application ID.
- [x] Create `<app-id>.desktop` with `Name`, `Exec`, `Icon`, `Type`, and an appropriate category such as `Utility;`.
- [+] Create `<app-id>.metainfo.xml` with name, concise summary, description, developer, project license, URLs, releases, branding colors, and screenshot references.
  - [x] Create and locally validate the application-ID-named MetaInfo file.
  - [ ] Push the screenshot and metadata commit so the remote screenshot URL resolves, then repeat network-enabled validation.
- [x] Produce application-ID-named icons in required scalable or PNG sizes, including at least 128×128. (64×64, 128×128, and 256×256 PNG)
- [x] Add a launcher script that starts the installed Python entry point from `/app`.

## 3. Manifest and Dependencies

- [x] Choose a maintained runtime/SDK that supplies Python, Tk/Tcl, and the required X11/Wayland libraries; document why it was selected. (`org.freedesktop.Platform`/`org.freedesktop.Sdk` 25.08, with Tcl/Tk and `_tkinter` bundled by the app.)
- [x] Create `<app-id>.yml` with `id`, `runtime`, `runtime-version`, `sdk`, `command`, modules, and build commands.
  - [x] Bundle pinned Tcl/Tk and a Python-version-matched `_tkinter` extension because Freedesktop 25.08 removed Tcl/Tk.
  - [x] Prove `python3 -m tkinter` opens successfully inside the completed Flatpak build. (Tcl/Tk 9.0.2)
- [x] Pin all downloaded sources to immutable release URLs and SHA-256 hashes; do not fetch dependencies during the build.
- [x] Package required Python dependencies from `requirements.txt` using generated, hash-pinned Flatpak modules. (No third-party Python packages are required.)
  - [x] Keep the first Flatpak build functional without the optional tray/audio packages by using the application fallbacks.
  - [x] Reconcile `requirements.txt` into required and optional dependency groups before packaging optional integrations. (`requirements-optional.txt`)
- [x] Install code under `/app/lib/pomodoro98`, the launcher under `/app/bin`, metadata under `/app/share/metainfo`, the desktop file under `/app/share/applications`, and icons under `/app/share/icons/hicolor`.
- [x] Minimize `finish-args`: request only display, audio, and notification/tray access that testing proves necessary. Avoid broad filesystem or host permissions. (Shared IPC required by X11, plus X11 and PulseAudio; no tray permission yet.)
- [x] Verify the app remains usable when system tray support or an audio backend is unavailable. (Sandbox import and launch passed with all optional backends absent.)

## 4. Build, Validate, and Test

- [x] Fix `make build` failing when rofiles-fuse cannot mount on the host.
  - [x] Reproduce the `fusermount` file-descriptor error.
  - [x] Use the supported non-FUSE build mode for build, rebuild, and install.
  - [x] Complete a build and verify the packaged Python/Tkinter import. (`make test`: Tcl/Tk 9.0, fallback import passed)

- [x] Install Flatpak, `flatpak-builder`, the Flathub remote, and `org.flatpak.Builder` on a Linux test system. (`org.flatpak.Builder` 1.4.9)
  - [x] Add repeatable Make targets for prerequisite setup, building, testing, source runs, user-local installation, installed-app runs, and uninstalling.
- [x] Build cleanly with `flatpak-builder --force-clean build-dir <app-id>.yml`.
- [+] Install and run the local build; test Start/Pause/Reset, focus/rest transitions, sounds, tray behavior, window icon/title, and clean shutdown on X11 and Wayland where possible.
  - [ ] Restore the local Flatpak installation before repeating desktop checks; `flatpak info io.github.phni.Pomodoro98` reported not installed on 2026-09-24.
  - [x] Install and launch the local build under X11/XWayland.
  - [x] Verify the user-local Flatpak desktop export and refresh the desktop application database for GNOME menu discovery.
  - [x] Match the Tk window class to the Flatpak application ID so GNOME associates running windows with the packaged icon.
  - [x] Verify packaged Tcl/Tk initialization and application import with optional backends absent.
  - [ ] Manually exercise Start/Pause/Reset, full focus/rest transitions, progress colors, sound fallback, title updates, and clean shutdown.
  - [ ] Test native X11 and at least one Wayland desktop through XWayland where available.
  - [ ] Decide whether to package and test optional tray integration in Flatpak.
- [x] Validate the desktop file with `desktop-file-validate`.
- [ ] Validate AppStream metadata with `flatpak-builder-lint appstream` and the complete repository with `flatpak-builder-lint manifest`.
  - [ ] Upgrade to Freedesktop 26.08; `flatpak-builder-lint manifest` warned `runtime-update-available-to-org.freedesktop.Platform-26.08` on 2026-10-17.
- [x] Test without network access and review sandbox permissions with `flatpak info --show-permissions <app-id>`. (Shared IPC plus `x11` and `pulseaudio` sockets.)
- [ ] Add CI that performs a clean Flatpak build and runs the Flathub linter for every pull request.

## 5. Flathub Publication

- [ ] Capture at least one current English Linux screenshot of only the application window; add a short caption in the MetaInfo file.
- [ ] Fork `flathub/flathub`, create a branch containing the manifest and required packaging files, and open a new-app pull request.
- [ ] In the submission, explain every sandbox permission and link the upstream repository, release tag, license, and test evidence.
- [ ] Resolve automated checks and reviewer feedback, then test the Flathub-generated build before approval.
- [ ] Accept the application repository invitation and configure Flathub verification using the matching source-hosting account or owned domain.
- [ ] After publication, verify the store listing, installation, launch, screenshots, metadata, and quality-status page.
- [ ] Establish an update process for new source tags, dependency hashes, runtime upgrades, screenshots, and release metadata.

## 6. Tech Debt

Audit 2026-10-15. Priority = (Impact + Risk) x (6 - Effort); scores in brackets.

### Phase 1: Quick Wins

- [ ] Remove the legacy `pomodoro98.py` entry point. [30]
  - [ ] Delete `pomodoro98.py` (it still references the non-existent `rest_end.wav`).
  - [ ] Update `AGENTS.md`, which still calls it the main implementation and asks to keep both variants aligned.
  - [ ] Drop it from the `make lint` `py_compile` step.
- [ ] Merge `sdd/` into `SDD/`; directories differing only by case collide on macOS and Windows checkouts. Update the path in `AGENTS.md`. [25]
- [ ] Make `VERSION` the single source of truth; read it at runtime instead of hardcoding `APP_VERSION`, and check the MetaInfo `<release>` matches during lint. [25]
- [ ] Strengthen `make lint`: add `ruff` (or pyflakes), and split Python checks from Flatpak checks so they run without Flatpak installed. [20]
- [ ] Treat `aplay` as failed when it exits non-zero so the Tk bell fallback still sounds. [15]
- [ ] Fix stale docstrings and comments (`icon.ico`, `click.wav`, "Stop button never closes the app"). [10]

### Phase 2: Testable Timer Core

- [ ] Extract timer state into a plain-Python `TimerModel` with a `Mode` enum, keeping Tk as a thin view. [24]
  - [ ] Replace the decrement-per-`after()` countdown with a monotonic deadline so the timer does not drift and survives suspend correctly.
  - [ ] Replace the `"focus"`/`"rest"`/`"stopped"` strings and the repeated mode-to-label/colour mappings. [16]
  - [ ] Share the duplicated callback-cancel logic in `pause()` and `reset()`.
  - [ ] Update the tray only when mode or displayed time changes; avoid the double update in `_switch_mode`. [10]
- [ ] Add `tests/` with pytest covering start, pause, reset, focus-to-rest, and cycle completion using a mocked clock. [24]
- [ ] Implement the CI item in section 4 with pytest and ruff, in addition to the Flatpak build and linter. [28]

### Phase 3: Ongoing

- [ ] Track upstream security releases for the bundled Tcl/Tk 9.0.x and the pinned `tkinter-standalone` commit as part of the section 5 update process. [18]

## References

- [Flatpak manifests](https://docs.flatpak.org/en/latest/manifests.html)
- [Flatpak requirements and conventions](https://docs.flatpak.org/en/latest/conventions.html)
- [Flathub submission requirements](https://docs.flathub.org/docs/for-app-authors/requirements)
- [Flathub MetaInfo guidelines](https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines)
- [Flathub linter](https://docs.flathub.org/docs/for-app-authors/linter)
