#!/bin/bash
echo "Checking for Paru installation..."
if ! command -v paru &> /dev/null; then
    source ./paru_update.sh 
    echo "Paru installation complete."
else
    echo "Paru is already installed."
fi

# Update system with Paru
paru -Syu

# You can add or remove programs from this list to customize your installation
aur_programs=(
    "visual-studio-code-bin"
    "oh-my-posh"
    "sublime-text-4"
    "wlogout"
)

echo "================================"
echo "    Installing AUR programs     "
echo "================================"
paru -S ${aur_programs[@]}