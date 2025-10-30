echo "================================"
echo "       Steam Installation       "
echo "================================"

# Enable Multilib
echo "Checking and enabling [multilib] repository in /etc/pacman.conf..."

sudo sed -i '/^#\[multilib\]/,/^#Include/s/^#//' /etc/pacman.conf

echo "[multilib] repository enabled."

echo "Synchronizing package databases and installing Steam..."
# The 'cd' command from your original script is not needed.
sudo pacman -Syu steam
echo "Steam installation completed."