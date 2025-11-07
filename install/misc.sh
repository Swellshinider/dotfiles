# You can add or remove programs from this list to customize your installation
misc_programs=(
    "unzip"
    "tar"
    "alacritty"
    "loupe"
    "swaync" 
    "copyq"
    "mpv" 
    "vlc" 
    "imagemagick"
    "grim" 
    "slurp"
    "vivaldi" 
    "nautilus" 
    "discord"
    "torbrowser-launcher"
    "fastfetch"
    "gimp"
    "bitwarden"

    # Development Tools
    "ffmpeg" 
    "dotnet-sdk"
    "nodejs"
    "npm"
    "python"
    "git"
    "wget"
    "curl"
)

sudo pacman -S --noconfirm ${misc_programs[@]}