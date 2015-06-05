BASH = """
function _passpie()
{
    COMPREPLY=()
    local word="${COMP_WORDS[COMP_CWORD]}"

    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=( $(compgen -W "{commands}" -- "$word") )
    else
        local words=("${COMP_WORDS[@]}")
        unset words[0]
        unset words[$COMP_CWORD]
        COMPREPLY=( $(compgen -W "$(grep -Ehrio '[A-Z0-9._%+-]+@[A-Z0-9.-]+(@[A-Z0-9_\-\.]+)?' {config_path})" -- "$word") )
    fi
}
complete -F _passpie 'passpie'
"""

ZSH = """
if [[ ! -o interactive ]]; then
    return
fi

compctl -K _passpie passpie

_passpie() {
  local words completions
  read -cA words

  if [ "${#words}" -eq 2 ]; then
    completions="{commands}"
  else
    completions="$(grep -Ehrio '\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+(@[A-Z0-9_\-\.]+)?\\b' {config_path})"
  fi

  reply=(${(ps:\n:)completions})
}
"""

SHELLS = ['zsh', 'bash']


def script(shell_name, config_path, commands):
    text = ''
    if shell_name == 'zsh':
        text = ZSH.replace('{commands}', '\n'.join(commands))
        text = text.replace('{config_path}', config_path)
    elif shell_name == 'bash':
        text = BASH.replace('{commands}', ' '.join(commands))
        text = text.replace('{config_path}', config_path)

    return text
