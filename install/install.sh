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

# Enable services
source ./up_services.sh

echo "Setup Complete! Please reboot your system."