# Passpie: Manage login credentials from terminal

## ![Passpie console interface](https://github.com/marcwebbie/passpie/raw/master/images/passpie.png)

[Passpie](https://marcwebbie.github.io/passpie) helps you manage login credentials from the terminal with a colorful andconfigurable interface. Password files are saved into yaml text files with passwords encrypted using [GnuPG](http://en.wikipedia.org/wiki/GNU_Privacy_Guard). Use your master passphrase to decrypt login credentials, copy passwords to clipboard syncronize them to a git repository and more...

## [![pypi](https://img.shields.io/pypi/v/passpie.svg?style=flat-square&label=latest%20version)](https://pypi.python.org/pypi/passpie) [![unix_build](https://img.shields.io/travis/marcwebbie/passpie/master.svg?style=flat-square&label=unix%20build)](https://travis-ci.org/marcwebbie/passpie) [![windows_build](https://img.shields.io/appveyor/ci/marcwebbie/passpie.svg?style=flat-square&label=windows%20build)](https://ci.appveyor.com/project/marcwebbie/passpie) [![coverage](https://img.shields.io/codecov/c/github/marcwebbie/passpie.svg?style=flat-square&label=coverage)](https://codecov.io/github/marcwebbie/passpie)


## Installation

```fish
pip install passpie
```

Or on a *mac*, with [homebrew](http://brew.sh):

```fish
brew install passpie
```

Or to install the *latest development* version:

```fish
pip install -U https://github.com/marcwebbie/passpie/tarball/master
```


## Quickstart

```fish
# initialize a passpie database
passpie init

# add some credentials
passpie add foo@example.com
passpie add bar@example.com

# add some credential with random passwords
passpie add bar@github.com --random
passpie add spam@egg --random
passpie add foo@github.com --random
passpie add bar@github.com --random

# add credentials with random password patterns
passpie add jane.doe@example.com --pattern '[0-9]{5}[a-z]{5}' --random
passpie add john.doe@example.com --pattern '[0-9]{5}[a-z]{5}' --random

# add spam@egg with random password and copy to clipboard
passpie add spam@egg.local --random --copy

# edit credential "foo@example.com"
passpie update foo@example.com

# copy password from credential "foo@example.com" to clipboard
passpie copy foo@example.com

# copy password to clipboard with clearing clipboard after 10 seconds
passpie copy foo@example.com --clear 10

# search credentials by string "exam"
passpie search exam

# search credentials using regular expressions
passpie search 'foo|bar'

# remove some credentials
passpie remove foo@example.com
passpie remove foo@github.com

# see the database change history
passpie log

# reset to a previous version of the database
passpie --reset-to 5

# check database status
passpie status

# print all credentials as a table with hidden passwords
passpie

# purge all credentials from database
passpie purge

# shows help. Option `--help`
passpie --help
```

## Commands

| Command        | Description                                           |
|----------------|-------------------------------------------------------|
| **`add`**      | Add new credential to database                        |
| **`complete`** | Generate completion scripts for shells                |
| **`copy`**     | Copy credential password to clipboard/stdout          |
| **`export`**   | Export credentials in plain text                      |
| **`import`**   | Import credentials from file                          |
| **`init`**     | Initialize new passpie database                       |
| **`log`**      | Shows passpie database changes history                |
| **`purge`**    | Remove all credentials from database                  |
| **`remove`**   | Remove credential                                     |
| **`reset`**    | Renew passpie database and re-encrypt all credentials |
| **`search`**   | Search credentials by regular expressions             |
| **`status`**   | Diagnose database for improvements                    |
| **`update`**   | Update credential                                     |

## Configuring passpie

### Global

You can override passpie default configuration with a **passpierc** file. Global user settings are read from the `~/.passpierc`

> Note that Passpie configuration files must be written as a valid [yaml](http://yaml.org/) file.

### Per-database

You can also add database specific configuration by creating a file called `.config` inside database directory. These files are automatically created when initializing databases.

### Example:

```yaml
path: ~/.passpie
homedir: ~/.gnupg
autopull: null
copy_timeout: 0
extension: .pass
genpass_pattern: "[a-z]{5} [-_+=*&%$#]{5} [A-Z]{5}"
headers:
  - name
  - login
  - password
  - comment
colors:
  login: green
  name: yellow
key_length: 4096
recipient: passpie@local
repo: true
short_commands: false
status_repeated_passwords_limit: 5
table_format: fancy_grid
```

### Fields

| Option                                                                                     | Description                                                                 |
|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| [path](./docs/configuration.md#path)                                                       | Path to default database                                                    |
| [homedir](./docs/configuration.md#homedir)                                                 | Path to gnupg homedir                                                       |
| [recipient](./docs/configuration.md#recipient)                                             | Default gpg recipient to encrypt/decrypt credentials using keychains        |
| [key_length](./docs/configuration.md#key_length)                                           | Key generation length                                                       |
| [repo](./docs/configuration.md#repo)                                                       | Create a git repo by default                                                |
| [autopull](./docs/configuration.md#autopull)                                               | Automatically pull changes from git remote repository                       |
| [copy_timeout](./docs/configuration.md#copy_timeout)                                       | Automatically clear password from clipboard                                 |
| [short_commands](./docs/configuration.md#short_commands)                                   | Use passpie commands with short aliases. Like `passpie a` for `passpie add` |
| [status_repeated_passwords_limit](./docs/configuration.md#status_repeated_passwords_limit) | Repeat credential fullname on status list                                   |
| [extension](./docs/configuration.md#extension)                                             | Credential files configurable extension                                     |
| [genpass_pattern](./docs/configuration.md#genpass_pattern)                                 | Regular expression pattern used to generate random passwords                |
| [headers](./docs/configuration.md#headers)                                                 | Credential columns to be printed                                            |
| [table_format](./docs/configuration.md#table_format)                                       | Defines how the Table is formated                                           |
| [colors](./docs/configuration.md#colors)                                                   | Column data colors                                                          |

> More configuration details on [configuring passpie](./docs/configuration.md)

## Tutorials

- [Diving into *fullname* syntax](./docs/fullname.md)
- [Grouping Credentials](./docs/grouping.md)
- [Multiple Databases](./docs/multiple_databases.md)
- [Syncing Credentials](./docs/syncing.md)
- [Version Control With Git](./docs/syncing.md)
- [Exporting Credentials](#)
- [Importing Credentials](./docs/importing.md)
- [Contributing](./docs/contributing.md)


## Common issues

#### GPG not installed. https://www.gnupg.org/

You don't have gpg installed or it is not working as expected

Make sure you have [gpg](https://www.gnupg.org/) installed:

Ubuntu:

```
sudo apt-get install gpg
```

OSX:

```
brew install gpg
```

#### xclip or xsel not installed

You don't have *copy to clipboard* support by default on some linux distributions.

Ubuntu:

```
sudo apt-get install xclip
```

#### passpie init hangs

Sometimes it takes a long time because of entropy on the host machine. It was noticed a long time on an ubuntu server(even more if it is a virtual machine). You could try using `haveged` to generate enough entropy.

On ubuntu:

```
sudo apt-get install haveged
```


## Licence [![license](http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](./LICENSE)

Copyright (c) 2014-2016 Marcwebbie, <http://github.com/marcwebbie>

> Full license here: [LICENSE](./LICENSE)
