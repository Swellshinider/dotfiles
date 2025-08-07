########################
# ZINIT PLUGIN MANAGER #
########################
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

# Clone if doesn't exist
if [ ! -d "$ZINIT_HOME" ]; then
    mkdir -p "$(dirname $ZINIT_HOME)"
    git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi

# Load zinit
source "${ZINIT_HOME}/zinit.zsh"

# Load plugins
zinit light zsh-users/zsh-syntax-highlighting

##############
# EXTRA APPS #
##############

# prompt manager
eval "$(oh-my-posh init zsh --config $HOME/.config/ohmyposh/ohmyposh.toml)"

###########
# ALIASES #
###########
alias ls='ls --color'
alias lsa='ls --color -lah'
alias cls='clear'