# You can add or remove programs from this list to customize your installation
misc_programs=(
    "git"
    "wget"
    "curl"
    "unzip"
    "tar"
    "alacritty"
    "loupe"
    "swaync" 
    "copyq"
    "mpv" 
    "vlc" 
    "ffmpeg" 
    "imagemagick"
    "grim" 
    "slurp"
    "vivaldi" 
    "nautilus" 
    "discord" 
    "torbrowser-launcher"
    "fastfetch"
)

sudo pacman -S --noconfirm ${misc_programs[@]}