# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project does not currently use semantic version tags for the dotfiles themselves.

## [Unreleased]

### Added

- Added `themectl`, a dotfiles theme manager with theme install, apply, preview, recover, scaffold, validation, and wallpaper rotation commands.
- Added an in-repo theme layout under `themes/` with `_base`, `default`, and `_template` entries.
- Added theme manager documentation in [`docs/theme-manager.md`](./theme-manager.md).

### Changed

- Switched Hyprland appearance and animation config to load the generated active theme from `~/.local/state/themectl/active`.
- Switched Waybar, SwayNC, Hyprpaper, Hyprlock, Wofi, and Wlogout entrypoints to launch through `themectl`.
- Switched Kitty and Alacritty to import the generated active theme files.
- Added the `Super+Shift+T` keybinding for the theme selector.
- Corrected the tracked GTK config paths from `gtl-*` to `gtk-*`.
