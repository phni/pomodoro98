# Flatpak Make workflow

Date: 2026-08-13

## Changes

- Add a repository-root Makefile as the consistent developer entry point.
- Add `setup-flatpak` to verify the host Flatpak/Flathub configuration and
  install the official Builder plus Freedesktop Platform/SDK 25.08.
- Add a normal build target that reuses the module cache and a full rebuild
  target that disables the module cache.
- Add source, shell, desktop, AppStream, and official Flathub manifest linting.
- Add non-interactive sandbox tests for Tkinter import, application import, and
  operation with optional integrations absent. Use `flatpak build` to execute
  them because the sandboxed Builder CLI returns a nonzero status after a
  successful `--run` command on this host.
- Add commands to run directly from source, install for the current user, run
  the installed Flatpak, uninstall it, and clear ignored build output.
- Document the workflow in the README and TODO checklist.

## Safety and scope

- The setup target installs only explicitly named Flathub components.
- Application installation uses `--user` and does not replace system packages.
- Build output is stored in ignored repository-local directories.
