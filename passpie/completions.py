BASH = """
function _passpie()
{
    COMPREPLY=()
    local word="${COMP_WORDS[COMP_CWORD]}"

    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=( $(compgen -W "remove update" -- "$word") )
    else
        local words=("${COMP_WORDS[@]}")
        unset words[0]
        unset words[$COMP_CWORD]
        COMPREPLY=( $(compgen -W "$(grep -r fullname $HOME/.passpie | sed 's/.*fullname:[ ]*//g')" -- "$word") )
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
    completions="remove\nupdate"
  else
    completions="$(grep -r fullname $HOME/.passpie | sed 's/.*fullname:[ ]*//g')"
  fi

  reply=(${(ps:\n:)completions})
}
"""
