#!/bin/bash
echo "================================"
echo "    NextCloud Client Setup      "
echo "================================"

# Create NextCloud Directory if it doesn't exist
NEXTCLOUD_DIR="$HOME/NextCloud"
if [ ! -d "$NEXTCLOUD_DIR" ]; then
    mkdir -p "$NEXTCLOUD_DIR"
    paru -S nextcloud-client
    echo "Created NextCloud directory at $NEXTCLOUD_DIR"
else
    echo "NextCloud directory already exists at $NEXTCLOUD_DIR"
fi