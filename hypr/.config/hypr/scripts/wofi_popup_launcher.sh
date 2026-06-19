#!/usr/bin/env sh

if pgrep -x wofi >/dev/null; then
  pkill -x wofi
  exit 0
fi

exec themectl launch launcher
