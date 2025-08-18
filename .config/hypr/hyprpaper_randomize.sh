
#!/usr/bin/env bash
set -euo pipefail

WALLPAPER_DIR="$HOME/Pictures/wallpapers/"
wp="$(find "$WALLPAPER_DIR" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) | shuf -n 1)"

# start hyprpaper if not running
pgrep -x hyprpaper >/dev/null || hyprpaper & disown
# tiny delay so hyprpaper is ready
sleep 0.3

# (optional) preload for instant display
hyprctl hyprpaper preload "$wp"

# set the same wallpaper on all monitors
hyprctl hyprpaper wallpaper ",$wp"
