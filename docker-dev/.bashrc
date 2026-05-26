# ============================================================
#  Shell Configuration — Dev Container (Ubuntu 24.04)
# ============================================================

export TERM=xterm-256color
export COLORTERM=truecolor
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups
shopt -s histappend

# ── pyenv ────────────────────────────────────────────────────
export PYENV_ROOT="/root/.pyenv"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
eval "$(pyenv init --path)" 2>/dev/null
eval "$(pyenv virtualenv-init -)" 2>/dev/null

# ── uv ───────────────────────────────────────────────────────
export PATH="/root/.local/bin:$PATH"
[ -f "$HOME/.local/bin/env" ] && . "$HOME/.local/bin/env" 2>/dev/null

# ── nvm / Node.js ────────────────────────────────────────────
export NVM_DIR="/root/.nvm"
[ -s "$NVM_DIR/nvm.sh" ]          && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# ── Prompt (256-color, git branch) ───────────────────────────
_git_branch() {
    local b
    b=$(git branch 2>/dev/null | grep '^\*' | sed 's/\* //')
    [ -n "$b" ] && printf ' \001\e[38;5;220m\002(%s)\001\e[0m\002' "$b"
}

_py_ver() {
    python --version 2>/dev/null | awk '{print " py:"$2}'
}

_node_ver() {
    node --version 2>/dev/null | sed 's/^/ node:/'
}

PS1='\[\e[38;5;46m\]╭─[\[\e[38;5;51m\]\u\[\e[38;5;46m\]@\[\e[38;5;226m\]docker\[\e[38;5;46m\]]\[\e[0m\] \[\e[38;5;33m\]\w\[\e[0m\]$(_git_branch)\n\[\e[38;5;46m\]╰─▶\[\e[0m\] '

# ── Colors ───────────────────────────────────────────────────
alias ls='ls --color=auto'
alias ll='ls -alFh --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias diff='diff --color=auto'
alias ip='ip --color=auto'

# ── Navigation ───────────────────────────────────────────────
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias work='cd /workspace/docnova'

# ── Git shortcuts ─────────────────────────────────────────────
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gpl='git pull'
alias gco='git checkout'
alias gb='git branch'
alias gd='git diff'
alias gl='git log --oneline --graph --decorate --color=auto'

# ── Python / uv ──────────────────────────────────────────────
alias python='python3'
alias pip='pip3'
alias uvs='uv pip install --system'

# ── Node / npm ───────────────────────────────────────────────
alias ni='npm install'
alias nr='npm run'
alias nb='npm run build'

# ── Utility ──────────────────────────────────────────────────
alias ports='ss -tulpn'
alias cls='clear'
alias h='history'
alias df='df -h'
alias du='du -sh'

# ── Welcome banner ───────────────────────────────────────────
_banner() {
    local PY ND UV
    PY=$(python --version 2>/dev/null | awk '{print $2}')
    ND=$(node --version 2>/dev/null)
    UV=$(uv --version 2>/dev/null | awk '{print $2}')
    echo -e "\e[38;5;51m"
    echo "  ██████╗ ███████╗██╗   ██╗"
    echo "  ██╔══██╗██╔════╝██║   ██║"
    echo "  ██║  ██║█████╗  ██║   ██║"
    echo "  ██║  ██║██╔══╝  ╚██╗ ██╔╝"
    echo "  ██████╔╝███████╗ ╚████╔╝ "
    echo "  ╚═════╝ ╚══════╝  ╚═══╝  "
    echo -e "\e[0m"
    echo -e "  \e[38;5;226mDev Container\e[0m — Ubuntu 24.04 (root)"
    echo -e "  \e[38;5;82m  Python : ${PY:-n/a}\e[0m"
    echo -e "  \e[38;5;178m⬡  Node   : ${ND:-n/a}\e[0m"
    echo -e "  \e[38;5;213m  uv     : ${UV:-n/a}\e[0m"
    echo -e "  \e[38;5;245m  Mount  : /workspace/docnova\e[0m"
    echo ""
}
_banner
