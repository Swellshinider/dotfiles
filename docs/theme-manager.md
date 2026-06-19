# Theme Manager

`themectl` manages full desktop themes for the Hyprland setup in this repository.

## Goals

- Keep tracked dotfiles stable in Git.
- Store themes in-repo under `themes/`.
- Generate the active theme in `~/.local/state/themectl/active`.
- Support preview with rollback.
- Keep theme authoring simple.

## Install

Stow the packages that provide the desktop entrypoints and then initialize the active state:

```bash
stow .local hypr kitty alacritty waybar swaync wofi wlogout gtk
themectl install
```

If you previously stowed the old GTK package paths, restow `gtk` after pulling this change because the tracked paths now use `gtk-3.0` and `gtk-4.0`.

## Commands

```bash
themectl install
themectl menu
themectl list
themectl current
themectl show default
themectl apply default
themectl preview default --timeout 30
themectl validate
themectl doctor
themectl recover
themectl new my-theme
themectl remove my-theme
themectl wallpaper next
```

## Runtime model

- Shared loader files stay in the normal config locations.
- `themectl` writes the merged active theme to `~/.local/state/themectl/active`.
- Hyprland sources the active appearance and animation files directly.
- Waybar, SwayNC, Hyprpaper, Hyprlock, Wofi, and Wlogout are launched through `themectl launch ...` so they can use generated config paths.
- Kitty and Alacritty import the generated theme files directly.

## Keybinding

The selector is bound to `Super+Shift+T`.

## Theme layout

`themes/_base/files` is the fallback layer.

`themes/default` is the shipped theme.

`themes/_template` is the scaffold copied by `themectl new`.

Supported override paths inside `themes/<theme-id>/files/`:

- `alacritty/theme.toml`
- `gtk/gtk-3.0/settings.ini`
- `gtk/gtk-4.0/settings.ini`
- `hypr/animations.conf`
- `hypr/appearance.conf`
- `hypr/hyprlock.conf`
- `hypr/hyprpaper.conf`
- `kitty/theme.conf`
- `swaync/config.json`
- `swaync/style.css`
- `waybar/config.jsonc`
- `waybar/style.css`
- `wofi/style.css`
- `wlogout/layout`
- `wlogout/style.css`

If a theme omits any of those files, the `_base` version is used.

## Manifest

Each theme needs a `theme.toml`:

```toml
schema = 1
id = "my-theme"
name = "My Theme"
description = "Short summary."

[preview]
image = "assets/preview.png"

[gtk]
theme = "Breeze"
color_scheme = "prefer-dark"

[assets]
wallpaper = "assets/wallpaper.png"
lockscreen_wallpaper = "assets/wallpaper.png"
wallpaper_dir = "~/Pictures/Wallpapers"
```

## Template variables

These placeholders are replaced when active files are generated:

- `{{theme.id}}`
- `{{theme.name}}`
- `{{theme.wallpaper}}`
- `{{theme.lockscreen_wallpaper}}`
- `{{theme.wallpaper_dir}}`
- `{{theme.preview_image}}`
- `{{home}}`
- `{{repo_root}}`
- `{{state_dir}}`
- `{{active_dir}}`

## Preview behavior

- `themectl preview <theme>` applies the theme without changing the confirmed theme in state.
- `themectl menu` can preview and then prompt for `Keep preview` or `Revert now`.
- If the preview is not confirmed, the watchdog reverts automatically when the timeout expires.
- `themectl recover` reverts an unfinished preview after a crash or interrupted session.

## Creating a new theme

1. Run `themectl new my-theme`.
2. Edit `themes/my-theme/theme.toml`.
3. Add only the files you want to override under `themes/my-theme/files/`.
4. Add preview and wallpaper assets if the theme needs them.
5. Run `themectl validate`.
6. Run `themectl preview my-theme --timeout 30` or open `themectl menu`.

