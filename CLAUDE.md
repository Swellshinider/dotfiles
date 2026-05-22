# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Arch Linux dotfiles managed with **GNU Stow**. Each top-level directory is a stow package whose internal tree mirrors `$HOME`. Run `stow <package>` from `~/.dotfiles` to symlink into place.

## Key Commands

```bash
# Stow a single package
stow <package>

# Stow all packages
stow */

# Install all recommended packages (Arch Linux)
cd install && source install.sh

# Install individual package groups
source install/drivers.sh    # Network, audio (PipeWire), Bluetooth, Intel GPU
source install/hyprland.sh   # Hyprland + Wayland ecosystem
source install/fonts.sh      # All fonts (JetBrainsMono, Noto, etc.)
source install/misc.sh       # ~25 programs (terminals, dev tools, media)
source install/paru.sh       # AUR helper + AUR packages
source install/steam.sh      # Steam (multilib repo)
```

## Architecture

**Window Manager**: Hyprland (Wayland) with modular config — `hypr/.config/hypr/hyprland.conf` sources 8 files from `confs/` (environment, windows, autostart, appearance, animations, input, bindings, permissions).

**Status Bar**: Waybar with island-style grouped modules. Custom `power-profile` script integrates via signal RTMIN+8.

**Shell**: Zsh with zinit plugin manager + Oh My Posh prompt.

**Terminals**: Kitty (primary) and Alacritty, both JetBrainsMono font, Tokyo Night theme.

**Power Management**: Full custom stack — `~/.local/bin/power-profile` script, root helper at `/usr/local/libexec/power-profile-apply`, sudoers rules, systemd restore service, and Waybar JSON output. The install is in `install/power_profiles.sh`.

**Custom Scripts**:

- `.local/bin/power-profile` — CPU power profiles (performance/balanced/powersave/ultra) with Waybar integration
- `.local/bin/run` — Quick compile-and-run for single C files
- `hypr/.config/hypr/scripts/battery_notify.sh` — Battery warnings at 20%/10%
- `hypr/.config/hypr/scripts/hyprpaper_randomize.sh` — Random wallpaper picker

## Configuration Patterns

- Theme: Tokyo Night across terminals and Waybar; JetBrainsMono is the universal font
- Hyprland autostarts: hyprlock, hypridle, blueman, nm-applet, swaync, copyq, waybar, bitwarden, discord, steam, nextcloud
- `.gitignore` excludes CopyQ data and VS Code internals (only `settings.json` and `keybindings.json` are tracked)

## Install Script Structure

All scripts in `install/` are sourced by `install.sh`. They use pacman (official repos) and Paru (AUR). `install/assets/` contains the power-profile root helper, systemd service, and sudoers config.
