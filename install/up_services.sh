#!/bin/bash

echo "================================"
echo "       Finalizing Setup         "
echo "================================"
sudo systemctl enable bluetooth.service
sudo systemctl enable NetworkManager
systemctl --user --now enable wireplumber