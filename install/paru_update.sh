#!/bin/bash
echo "================================"
echo "       Paru Installation        "
echo "================================"
# Install dependencies for building Paru
sudo pacman -S --noconfirm git base-devel rustup
rustup default stable

git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si
cd ..
rm -rf paru