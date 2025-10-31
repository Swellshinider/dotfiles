#!/bin/bash
# You can add or remove programs from this list to customize your installation
hyprland_programs=(
    "hyprland"
    "xorg-xwayland"
    "xdg-desktop-portal-hyprland"
    "xdg-desktop-portal-gtk"
    "waybar"
    "hyprpaper"
    "hypridle"
    "hyprlock"
    "hyprpicker"
    "wl-clipboard"
    "hyprshot"
    "wofi"
)

echo "================================"
echo "     Hyprland Installation      "
echo "================================"
sudo pacman -S --noconfirm ${hyprland_programs[@]}