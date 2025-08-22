#!/usr/bin/env bash
set -euo pipefail

WALLPAPER_DIR="$HOME/Pictures/wallpapers"

# pick a random image
wp="$(find -L "$WALLPAPER_DIR" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) | shuf -n 1)"

[ -n "${wp:-}" ] || { echo "No wallpapers found in $WALLPAPER_DIR"; exit 0; }

# start hyprpaper if not running
pgrep -x hyprpaper >/dev/null || hyprpaper & disown

# wait for hyprpaper to be ready
for i in {1..50}; do
  if hyprctl hyprpaper list >/dev/null 2>&1; then break; fi
  sleep 0.05
done

# preload and set (all monitors)
hyprctl hyprpaper preload "$wp"
hyprctl hyprpaper wallpaper ",$wp"