# Pomodoro98 Flatpak Publication TODO

## 1. Project Readiness

- [x] Choose the canonical entry point (`pomodoro98.py` or `pomodoro98_2.py`) and remove or clearly document the other variant. (`pomodoro98_2.py`)
- [x] Add an open-source `LICENSE`; record its SPDX identifier for AppStream metadata. (`MIT`)
- [x] Complete `README.md` with run instructions, supported Linux desktops, screenshots, and maintainer contact details.
- [x] Add versioning and create a tagged source release; Flathub expects a meaningful development history and standard releases. (`v0.1.0`)
- [x] Make asset paths independent of the current working directory (resolve them relative to the installed application).
- [x] Confirm focus/rest sound filenames match the files actually shipped. (`focus_end.wav`, `reset_end.wav`)

## 2. Flatpak Identity and Desktop Integration

- [ ] Select a permanent reverse-DNS application ID. Prefer `io.github.<owner>.Pomodoro98` if this repository will be hosted on GitHub; confirm the owner and repository URL first.
- [ ] Rename exported files to match the application ID.
- [ ] Create `<app-id>.desktop` with `Name`, `Exec`, `Icon`, `Type`, and an appropriate category such as `Utility;`.
- [ ] Create `<app-id>.metainfo.xml` with name, concise summary, description, developer, project license, URLs, releases, branding colors, and screenshot references.
- [ ] Produce application-ID-named icons in required scalable or PNG sizes, including at least 128×128.
- [x] Add a launcher script that starts the installed Python entry point from `/app`.

## 3. Manifest and Dependencies

- [ ] Choose a maintained runtime/SDK that supplies Python, Tk/Tcl, and the required X11/Wayland libraries; document why it was selected.
- [ ] Create `<app-id>.yml` with `id`, `runtime`, `runtime-version`, `sdk`, `command`, modules, and build commands.
- [ ] Pin all downloaded sources to immutable release URLs and SHA-256 hashes; do not fetch dependencies during the build.
- [ ] Package required Python dependencies from `requirements.txt` using generated, hash-pinned Flatpak modules.
- [ ] Install code under `/app/lib/pomodoro98`, the launcher under `/app/bin`, metadata under `/app/share/metainfo`, the desktop file under `/app/share/applications`, and icons under `/app/share/icons/hicolor`.
- [ ] Minimize `finish-args`: request only display, audio, and notification/tray access that testing proves necessary. Avoid broad filesystem or host permissions.
- [ ] Verify the app remains usable when system tray support or an audio backend is unavailable.

## 4. Build, Validate, and Test

- [ ] Install Flatpak, `flatpak-builder`, the Flathub remote, and `org.flatpak.Builder` on a Linux test system.
- [ ] Build cleanly with `flatpak-builder --force-clean build-dir <app-id>.yml`.
- [ ] Install and run the local build; test Start/Stop, focus/rest transitions, sounds, tray behavior, window icon/title, and clean shutdown on X11 and Wayland where possible.
- [ ] Validate the desktop file with `desktop-file-validate`.
- [ ] Validate AppStream metadata with `flatpak-builder-lint appstream` and the complete repository with `flatpak-builder-lint manifest`.
- [ ] Test without network access and review sandbox permissions with `flatpak info --show-permissions <app-id>`.
- [ ] Add CI that performs a clean Flatpak build and runs the Flathub linter for every pull request.

## 5. Flathub Publication

- [ ] Capture at least one current English Linux screenshot of only the application window; add a short caption in the MetaInfo file.
- [ ] Fork `flathub/flathub`, create a branch containing the manifest and required packaging files, and open a new-app pull request.
- [ ] In the submission, explain every sandbox permission and link the upstream repository, release tag, license, and test evidence.
- [ ] Resolve automated checks and reviewer feedback, then test the Flathub-generated build before approval.
- [ ] Accept the application repository invitation and configure Flathub verification using the matching source-hosting account or owned domain.
- [ ] After publication, verify the store listing, installation, launch, screenshots, metadata, and quality-status page.
- [ ] Establish an update process for new source tags, dependency hashes, runtime upgrades, screenshots, and release metadata.

## References

- [Flatpak manifests](https://docs.flatpak.org/en/latest/manifests.html)
- [Flatpak requirements and conventions](https://docs.flatpak.org/en/latest/conventions.html)
- [Flathub submission requirements](https://docs.flathub.org/docs/for-app-authors/requirements)
- [Flathub MetaInfo guidelines](https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines)
- [Flathub linter](https://docs.flathub.org/docs/for-app-authors/linter)
