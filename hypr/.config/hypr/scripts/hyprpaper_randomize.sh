#!/usr/bin/env bash
set -euo pipefail

WALLPAPER_DIR="$HOME/Pictures/Wallpapers"

# pick a random image
shopt -s nullglob globstar
wp="$(printf '%s\n' "$WALLPAPER_DIR"/**/*.{png,jpg,jpeg,webp,PNG,JPG,JPEG,WEBP} | shuf -n 1)"

[ -n "${wp:-}" ] || { echo "No wallpapers found in $WALLPAPER_DIR"; exit 0; }

# start hyprpaper if not running
pgrep -x hyprpaper >/dev/null || { hyprpaper & disown; sleep 1; }

# set wallpaper directly (hyprpaper >= 0.8)
hyprctl hyprpaper wallpaper ",$wp"
