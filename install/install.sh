# Pacman update
sudo pacman -Syu

source ./paru.sh
source ./hyprland.sh
source ./misc.sh
source ./themes.sh
source ./fonts.sh
source ./nextcloud.sh

echo "================================"
echo "       Finalizing Setup         "
echo "================================"
sudo systemctl enable bluetooth.service
sudo systemctl enable NetworkManager

echo "Setup Complete! Please reboot your system."