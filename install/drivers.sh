#!/bin/bash
# You can add or remove programs from this list to customize your installation
driver_programs=(
    "gst-plugin-pipewire" 
    "gst-libav" 
    "gst-plugins-bad" 
    "gst-plugins-good"
    "gst-plugins-ugly"
    "pipewire"
    "pipewire-pulse" 
    "pipewire-alsa" 
    "wireplumber"
    "bluez" 
    "bluez-utils" 
    "blueman" 
    "pamixer" 
    "pavucontrol"
    "sof-firmware"
    "alsa-utils"

    # Intel graphics drivers
    "xf86-video-intel"
    "mesa"
    "lib32-mesa"
    "vulkan-intel"
    "lib32-vulkan-intel"
    "intel-media-driver"
    "intel-gpu-tools"
    "libva-intel-driver"
    "libva-utils"
    "intel-ucode"

    # AMD graphics drivers
    # "xf86-video-amdgpu"
    # "mesa"
    # "lib32-mesa"
    # "vulkan-radeon"
    # "lib32-vulkan-radeon"
    # "amdvlk"

    # NVIDIA graphics drivers
    # "nvidia"
    # "nvidia-utils"
    # "nvidia-settings"
    # "lib32-nvidia-utils"
    # "nvidia-dkms"
)

echo "================================"
echo "     Drivers Installation       "
echo "================================"
sudo pacman -S --noconfirm ${driver_programs[@]}
