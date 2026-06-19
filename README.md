# My Dotfiles

My personal dotfiles for Arch Linux, managed using [GNU Stow](https://www.gnu.org/software/stow/).

![Desktop Preview](./docs/desktop.png)

## Pre-configuration

1. Install stow

   ```bash
   sudo pacman -S stow
   ```

2. Then clone this repo

   ```bash
   git clone https://github.com/Swellshinider/dotfiles.git ~/.dotfiles
   cd ~/.dotfiles
   ```

3. Stow any package that you want, example:

   ```bash
   stow hypr
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

## Easy

Just reboot your system and test!

```bash
sudo reboot
```
