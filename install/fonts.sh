#!/bin/bash
# You can add or remove programs from this list to customize your installation
fonts=(
    noto-fonts
    noto-fonts-emoji
    noto-fonts-cjk
    ttf-liberation
    ttf-dejavu
    ttf-fira-code
    ttf-roboto
    adobe-source-han-sans-otc-fonts
    woff2-font-awesome
)

echo "================================"
echo "       Fonts Installation       "
echo "================================"
sudo pacman -S --noconfirm ${fonts[@]}