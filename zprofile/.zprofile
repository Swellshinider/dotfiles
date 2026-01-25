if [[ -z $DISPLAY ]] && [[ $(tty) == /dev/tty1 ]]; then
    exec start-hyprland
fi

export QT_QPA_PLATFORMTHEME=qt5ct