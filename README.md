# My Dotfiles

My personal dotfiles for Arch Linux, managed using [GNU Stow](https://www.gnu.org/software/stow/).

![Preview](./docs/image.png)

## Pre-configuration

1) Install stow
```bash
sudo pacman -S stow
```

2) Then clone this repo

```bash
git clone https://github.com/Swellshinider/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
```

3) Stow any package that you want, example:

```bash
stow hypr
```

## Hyprland autostart (optional)

1) Configure a service so TTY will  lauch hyprland
```bash
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo nano /etc/systemd/system/getty@tty1.service.d/autologin.conf
```
2) Add this three lines into the file (replace **USERNAME** by your username):
```text
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin USERNAME --noclear %I $TERM
```

## Installing packages (optional)

Execute this to install all the recommended packages:

```bash
cd ~.dotfiles/install/
source install.sh
```
Or you can just check the files in **[install](./install/)** directory to get whatever you want.

## Setup zsh as default shell (optional)

```bash
chsh -s $(which zsh)
```

## Easy!

Just reboot your system and test!

```bash
sudo reboot
```