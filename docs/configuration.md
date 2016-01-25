# Configuring passpie

You can override default passpie configuration with a `.passpierc` file in your home directory. Passpie configuration files must be written as a valid [yaml](http://yaml.org/) file.

> You can also add database specific configuration by creating a file called `.config`.

## Example `~/.passpierc`:

```yaml
path: ~/.passpie
homedir: ~/.gnupg
autopull: false
copy_timeout: 0
extension: .pass
genpass_length: 32
genpass_symbols: _-#+=
headers:
  - name
  - login
  - password
  - comment
colors:
  login: green
  name: yellow
key_length: 4096
recipient: null
repo: true
short_commands: false
status_repeated_passwords_limit: 5
table_format: fancy_grid
```

| Option                          | Default                              | Description                                                                 |
|---------------------------------|--------------------------------------|-----------------------------------------------------------------------------|
| path                            | ~/.passpie                           | Path to default database                                                    |
| homedir                         | ~/.gnupg                             |                                                                             |
| recipient                       | null                                 | Default gpg recipient to encrypt/decrypt credentials                        |
| key_length                      | 4096                                 | Key generation length                                                       |
| repo                            | true                                 | Create a git repo by default                                                |
| autopull                        | false                                | Automatically pull changes from git remote repository                       |
| copy_timeout                    | 0                                    | Automatically clear copy to clipboard commands                              |
| short_commands                  | false                                | Use passpie commands with short aliases. Like `passpie a` for `passpie add` |
| status_repeated_passwords_limit | 5                                    | Repeat credential fullname on status list                                   |
| extension                       | .pass                                | Credential files extension                                                  |
| genpass_length                  | 32                                   | Length of randomly generated passwords with option `--random`               |
| genpass_symbols                 | _-#+=                                | Symbols used on random password generation                                  |
| headers                         | [name, login, password, comment]     | Values: (name, login, password, comment, fullname)                          |
| table_format                    | fancy_grid                           | Table format when listing credentials                                       |
| colors                          | {'login': 'green', 'name': 'yellow'} | Values: (green, red, blue, white, cyan, magenta, yellow)                    |
