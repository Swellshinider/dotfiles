#!/usr/bin/env sh

if pgrep -x wofi >/dev/null; then
  pkill -x wofi
  exit 0
fi

# Execute wofi in the top left corner
exec wofi \
  --show drun \
  --prompt "" \
  --location top_left \
  --xoffset 10 \
  --yoffset 5 \
  --width 800 \
  --height 420
