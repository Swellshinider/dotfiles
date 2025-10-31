#!/bin/bash

# Pacman update
sudo pacman -Syu

# Install drivers, themes, and fonts (Important to do before other installations)
source ./drivers.sh
source ./themes.sh
source ./fonts.sh

# Install Paru and AUR programs
source ./paru.sh

# Install Hyprland and related programs
source ./hyprland.sh

# Install miscellaneous programs
source ./misc.sh
source ./steam.sh
source ./nextcloud.sh

echo "================================"
echo "       Finalizing Setup         "
echo "================================"
sudo systemctl enable bluetooth.service
sudo systemctl enable NetworkManager
systemctl --user --now enable wireplumber.services

echo "Setup Complete! Please reboot your system."