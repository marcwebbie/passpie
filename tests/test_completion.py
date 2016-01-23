import tempfile

from passpie import completion


def test_script_returns_zsh_script_when_zsh_shell_name(mocker):
    shell_name = 'zsh'
    config_path = tempfile.gettempdir()
    commands = ['add', 'remove', 'update', 'remove', 'search']
    text = completion.script(shell_name=shell_name,
                             config_path=config_path,
                             commands=commands)

    for line in completion.ZSH.split('\n')[:3]:
        assert line in text


def test_script_returns_fish_script_when_fish_shell_name(mocker):
    shell_name = 'fish'
    config_path = tempfile.gettempdir()
    commands = ['add', 'remove', 'update', 'remove', 'search']
    text = completion.script(shell_name=shell_name,
                             config_path=config_path,
                             commands=commands)

    for line in completion.FISH.split('\n')[9:28]:
        assert line in text


def test_script_returns_bash_script_when_bash_shell_name(mocker):
    shell_name = 'bash'
    config_path = tempfile.gettempdir()
    commands = ['add', 'remove', 'update', 'remove', 'search']
    text = completion.script(shell_name=shell_name,
                             config_path=config_path,
                             commands=commands)

    for line in completion.BASH.split('\n')[:3]:
        assert line in text
