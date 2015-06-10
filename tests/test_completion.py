from passpie import completion


def test_script_returns_zsh_script_when_zsh_shell_name(mocker):
    shell_name = 'zsh'
    config_path = '/tmp'
    commands = ['add', 'remove', 'update', 'remove', 'search']
    text = completion.script(shell_name=shell_name,
                             config_path=config_path,
                             commands=commands)

    for line in completion.ZSH.split('\n')[:3]:
        assert line in text


def test_script_returns_bash_script_when_bash_shell_name(mocker):
    shell_name = 'bash'
    config_path = '/tmp'
    commands = ['add', 'remove', 'update', 'remove', 'search']
    text = completion.script(shell_name=shell_name,
                             config_path=config_path,
                             commands=commands)

    for line in completion.BASH.split('\n')[:3]:
        assert line in text
