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
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions

# Config plugins
autoload -U compinit && compinit
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'
HISTSIZE=5000
HISTFILE=~/.zsh_history
SAVEHIST=$HISTSIZE
HISTDUP=erase
setopt appendhistory
setopt sharehistory
setopt hist_ignore_space
setopt hist_ignore_all_dups
setopt hist_save_no_dups
setopt hist_ignore_dups
setopt hist_find_no_dups

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
alias poff='sync && sudo systemctl poweroff'
alias vim='nvim'

###############
# KEYBINDINGS #
###############
bindkey -e
bindkey '^p' history-search-backward
bindkey '^n' history-search-forward


# Load Angular CLI autocompletion.
source <(ng completion script)
