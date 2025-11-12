#!/bin/bash
# You can add or remove programs from this list to customize your installation
fonts=(
    "noto-fonts"
    "noto-fonts-emoji"
    "noto-fonts-cjk"
    "ttf-jetbrains-mono-nerd"
    "ttf-liberation"
    "ttf-dejavu"
    "ttf-roboto"
    "ttf-fira-code"
    "adobe-source-han-sans-otc-fonts"
    "woff2-font-awesome"
)

echo "================================"
echo "       Fonts Installation       "
echo "================================"
sudo pacman -S --noconfirm ${fonts[@]}
fc-cache -f -v