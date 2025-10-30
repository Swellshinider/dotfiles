# Paru dependencies
sudo pacman -S base-devel
sudo pacman -S rustup
rustup default stable

if ! command -v paru &> /dev/null; then
    echo "Paru not found. Installing paru..."
    git clone https://aur.archlinux.org/paru.git ~/paru
    cd ~/paru
    makepkg -si
    cd ~
    rm -rf ~/paru
    echo "Paru installation complete."
else
    echo "Paru is already installed."
fi

# Update system with Paru
paru -Syu

# AUR Programs
paru -S visual-studio-code-bin oh-my-posh sublime-text-4 1password