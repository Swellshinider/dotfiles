#!/usr/bin/env bash
set -euo pipefail

WALLPAPER_DIR="$HOME/Pictures/wallpapers/"
wp="$(find "$WALLPAPER_DIR" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) | shuf -n 1)"

# start hyprpaper if not running
pgrep -x hyprpaper >/dev/null || hyprpaper & disown
# tiny delay so hyprpaper is ready
sleep 0.1

# preload
hyprctl hyprpaper preload "$wp"

# set
hyprctl hyprpaper wallpaper ",$wp"
