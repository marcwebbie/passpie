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
        COMPREPLY=( $(compgen -W "$(grep -EhriIo '[A-Z0-9._%+-]+@[A-Z0-9.-]+(@[A-Z0-9_\-\.]+)?' {config_path})${IFS}\
                                  $(ls -1 {config_path})" -- "$word") )
    fi
}
complete -F _passpie 'passpie'
"""

FISH = """
function _passpie_credentials
  grep -EhriIo '[A-Z0-9._%+-]+@[A-Z0-9.-]+(@[A-Z0-9_\-\.]+)?' {config_path}
end

function _passpie_credential_names
  ls -1 {config_path}
end

function _passpie_needs_command
  set cmd (commandline -opc)
  if [ (count $cmd) -eq 1 -a $cmd[1] = 'passpie' ]
    return 0
  end
  return 1
end

function _passpie_using_command
  set cmd (commandline -opc)
  if [ (count $cmd) -gt 1 ]
    for arg in $argv
      if [ $arg = $cmd[2] ]
        return 0
      end
    end
  end
  return 1
end

complete -f -c passpie -n '_passpie_needs_command' -a '{commands}' --description 'Manage a credential'
complete -f -c passpie -n '_passpie_using_command {commands}' -a '(_passpie_credentials)
                                                                  (_passpie_credential_names)' --description 'Credential'
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
    completions="$(grep -EhriIo '\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+(@[A-Z0-9_\-\.]+)?\\b' {config_path})${IFS}\
                 $(ls -1 {config_path})"
  fi

  reply=(${(ps:\n:)completions})
}
"""

SHELLS = ['zsh', 'fish', 'bash']


def script(shell_name, config_path, commands):
    text = ''
    if shell_name == 'zsh':
        text = ZSH.replace('{commands}', '\n'.join(commands))
        text = text.replace('{config_path}', config_path)
    elif shell_name == 'fish':
        text = FISH.replace('{commands}', ' '.join(commands))
        text = text.replace('{config_path}', config_path)
    elif shell_name == 'bash':
        text = BASH.replace('{commands}', ' '.join(commands))
        text = text.replace('{config_path}', config_path)

    return text
