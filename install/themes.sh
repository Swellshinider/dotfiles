# You can add or remove programs from this list to customize your installation
themes=(
    "breeze"
    "breeze-gtk"
    "qt5ct"
    "qt6ct"
)

echo "================================"
echo "       Theme Installation       "
echo "================================"
sudo pacman -S ${themes[@]}