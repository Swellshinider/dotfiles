# Pacman update
sudo pacman -Syu

# Yay dependencies
sudo pacman -S base-devel

# Install yay if not installed
echo "================================"
echo "Checking for yay installation..."
echo "================================"

if ! command -v yay &> /dev/null; then
    git clone https://aur.archlinux.org/yay.git ~/yay_temp
    cd ~/yay_temp
    makepkg -si
    cd ~
    rm -rf ~/yay_temp
else
    echo "yay is already installed"
    yay -Syu
fiX

echo "================================"
echo "    Hyprland and dependencies   "
echo "================================"
sudo pacman -S hyprland xorg-xwayland xdg-desktop-portal-hyprland xdg-desktop-portal-gtk waybar hyprpaper hypridle hyprlock hyprpicker wl-clipboard hyprshot wofi 

echo "================================"
echo "     Miscellaneous Programs     "
echo "================================"
sudo pacman -S git wget curl unzip tar
sudo pacman -S alacritty
sudo pacman -S pipewire bluez bluez-utils blueman swaync copyq
sudo pacman -S gst-plugin-pipewire gst-libav gst-plugins-bad gst-plugins-good gst-plugins-ugly
sudo pacman -S mpv vlc ffmpeg imagemagick
sudo pacman -S pamixer pavucontrol
sudo pacman -S grim slurp
sudo pacman -S vivaldi nautilus discord

yay -S visual-studio-code-bin
yay -S oh-my-posh
yay -S sublime-text-4

# Themes
echo "================================"
echo "       Theme Installation       "
echo "================================"
sudo pacman -S breeze breeze-gtk
sudo pacman -S qt5ct qt6ct

echo "================================"
echo "       Font Installation        "
echo "================================"
sudo pacman -S noto-fonts noto-fonts-emoji noto-fonts-cjk ttf-liberation ttf-dejavu ttf-fira-code ttf-roboto adobe-source-han-sans-otc-fonts woff2-font-awesome

echo "================================"
echo "       Finalizing Setup         "
echo "================================"
sudo systemctl enable bluetooth.service
sudo systemctl enable NetworkManager
echo "Setup Complete! Please reboot your system."