# Flatpak identity and desktop integration

Date: 2026-08-13

## Changes

- Select `io.github.phni.Pomodoro98` as the permanent application ID, matching
  the `phni/pomodoro98` GitHub repository and Flathub's code-hosting ID rules.
- Add the application ID to the maintained Python entry point.
- Add an application-ID-named desktop file with the installed launcher command,
  icon, user-facing description, utility/office categories, and search keywords.
- Add application-ID-named AppStream MetaInfo with MIT project licensing,
  CC0-1.0 metadata licensing, developer identity, URLs, release information,
  screenshot, brand colors, launchable desktop ID, and OARS content rating.
- Add application-ID-named 64×64, 128×128, and 256×256 PNG icons under a
  Flatpak-ready hicolor directory layout.
- Preserve the original icon exactly using nearest-neighbor enlargement. An AI
  upscale was evaluated and rejected because it introduced gradients and
  geometry changes inconsistent with the source pixel art.

## Verification

- `desktop-file-validate flatpak/io.github.phni.Pomodoro98.desktop`
- `appstreamcli validate --pedantic flatpak/io.github.phni.Pomodoro98.metainfo.xml`
- Confirm all exported filenames and internal references use the application ID.
- Confirm each icon is square and has the dimensions declared by its directory.

## Pending sub-action

- Push the screenshot and metadata to GitHub, then repeat network-enabled
  AppStream validation so its URL reachability checks can succeed. This is
  recorded beneath the MetaInfo parent item in `SDD/todo.md`.
