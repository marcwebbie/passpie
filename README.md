# Passpie: Manage login credentials from terminal

[Passpie](https://marcwebbie.github.io/passpie) lets you manage login credentials from the terminal with a coloroful/configurable cli interface. Password files are saved into yaml text files with passwords as [GnuPG](http://en.wikipedia.org/wiki/GNU_Privacy_Guard) encrypted strings. Use your master passphrase to decrypt login credentials, copy passwords to clipboard and more...

![Passpie console interface](https://github.com/marcwebbie/passpie/raw/master/images/passpie.png)

> Passpie is built with [Click](http://click.pocoo.org) and [Tabulate](https://pypi.python.org/pypi/tabulate) for its interface, [TinyDB](https://github.com/msiemens/tinydb) for its database and [python-gnupg](https://github.com/isislovecruft/python-gnupg) for its encryption using *gpg*. Passpie is also inspired by great cli applications like [git](https://github.com/git/git) and [httpie](http://httpie.org/)

-----

[![pypi](https://img.shields.io/pypi/v/passpie.svg?style=flat-square&label=latest%20version)](https://pypi.python.org/pypi/passpie)
[![unix_build](https://img.shields.io/travis/marcwebbie/passpie/master.svg?style=flat-square&label=unix%20build)](https://travis-ci.org/marcwebbie/passpie)
[![windows_build](https://img.shields.io/appveyor/ci/marcwebbie/passpie.svg?style=flat-square&label=windows%20build)](https://ci.appveyor.com/project/marcwebbie/passpie)
[![coverage](https://img.shields.io/codecov/c/github/marcwebbie/passpie.svg?style=flat-square&label=coverage)](https://codecov.io/github/marcwebbie/passpie)

-----


## Features

+ [x] Console interface
+ [x] Manage multiple databases
+ [x] Add, update, remove credentials
+ [x] Copy passwords to clipboard
+ [x] List credentials as a table
+ [x] List credentials with a colored output
+ [x] Search credentials by name, login or comments
+ [x] Search with regular expression
+ [x] Group credentials by name
+ [x] [Configuration](#configuring-passpie-with-passpierc) from file. `~/.passpie`
+ [x] Change passphrase and re-encrypt database
+ [x] Export Passpie database to plain text file
+ [x] Import plain text Passpie database
+ [x] Import credentials from [Pysswords](https://github.com/marcwebbie/pysswords)
+ [x] Randomly generated credential passwords
+ [x] Configurable random password generation
+ [x] Generate database status report
+ [x] Bulk remove credentials
+ [x] Bash/Zsh [completion](#passpie-completion)

Planned features:

+ [ ] Undo/Redo updates to the database
+ [ ] Bulk update credentials
+ [ ] Import plain text credentials from [Keepass](http://keepass.info/)
+ [ ] Import plain text credentials from [1Password](https://agilebits.com/onepassword)

## Quickstart

```bash
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

# add spam@egg with random password and copy to clipboard
passpie add spam@egg.local --random --copy

# edit credential "foo@example.com"
passpie update foo@example.com

# copy password from credential "foo@example.com" to clipboard
passpie copy foo@example.com

# search credentials by string "exam"
passpie search exam

# search credentials using regular expressions
passpie search 'foo|bar'

# remove some credentials
passpie remove foo@example.com
passpie remove foo@github.com

# check database status
passpie status

# print all credentials as a table with hidden passwords
passpie

# shows help. Option `--help`
passpie --help
```

## Installation

### Dependencies

+ `[Linux, OSX, Windows]` [GnuPG](https://www.gnupg.org/)
+ `[Linux]` [xclip](http://linux.die.net/man/1/xclip) or [xsel](http://linux.die.net/man/1/xsel)

### Stable version

#### Using [pip](http://pip.readthedocs.org/en/latest/installing.html)

```bash
pip install passpie
```

#### On a mac you can install it with [homebrew](http://brew.sh)

```bash
brew install passpie
```

### Development version

The **latest development version** can be installed directly from GitHub:

```bash
pip install --upgrade https://github.com/marcwebbie/passpie/tarball/master
```

## Tutorials

### Diving into *fullname* syntax

Passpie credentials are referenced by `fullname`. fullname syntax handles login and name for credentials in one go for faster adding and querying of credentials.

#### Structure of a fullname

Fullnames are composed of `login`@`name`. Login is optional. If you don't pass any login when adding new credentials, credential login will be replaced by a `_` character:

```bash
passpie add @banks/mybank --password 1234
passpie add @banks/myotherbank --password 5678
```

Listing credentials:

```bash
$ passpie
=================  =======  ==========  =========
Name               Login    Password    Comment
=================  =======  ==========  =========
banks/mybank       _        *****
banks/myotherbank  _        *****
=================  =======  ==========  =========
```

Since `login` is optional. You can query credentials using only name syntax, for example to update credential `@banks/mybank`:

```bash
passpie update @banks/mybank --random
```

Or even better, without using the `@` notation:

```bash
passpie update banks/mybank --random
```

### Syncing your database

#### Dropbox

With default path `~/.passpie` and a Dropbox shared directory on path `~/Dropbox`

```bash
mv ~/.passpie ~/Dropbox/passpie    # move passpie db to Dropbox
ln -s ~/Dropbox/passpie ~/.passpie # make a link to the db
```

#### Google Drive

With default path `~/.passpie` and a Google Drive shared directory on path `~/GoogleDrive`

```bash
mv ~/.passpie ~/GoogleDrive/passpie   # move passpie db to Google Drive
ln -s ~/GoogleDrive/passpie ~.passpie # make a link to the db
```

### Exporting a passpie database

```bash
passpie export passpie.db
```

### Importing a passpie database

```bash
passpie import passpie.db
```

### Grouping credentials by name

Passpie credentials handles multiple logins for each name which groups credentials by name:

```bash
# add some credentials
passpie add jonh@example.com --comment "Jonh main mail" --random
passpie add doe@example.com --comment "No comment" --random
```

Listing credentials:

```bash
$ passpie
===========  =======  ==========  ===============
name         login    password    comment
===========  =======  ==========  ===============
example.com  doe      *****       No comment
example.com  jonh     *****       Jonh main email
===========  =======  ==========  ===============
```

#### Subgroups

Fullname syntax supports subgrouping of credentials by name

```
passpie add foo@opensource/github.com --random
passpie add foo@opensource/python.org --random
passpie add foo@opensource/bitbucket.org --random
passpie add foo@opensource/npm.org --random
```

Listing credentials:

```
$ passpie
========================  =======  ==========  =========
Name                      Login    Password    Comment
========================  =======  ==========  =========
opensource/bitbucket.org  foo      *****
opensource/github.com     foo      *****
opensource/npm.org        foo      *****
opensource/python.org     foo      *****
========================  =======  ==========  =========
```

### Multiple databases

Sometimes it is useful to have multiple databases with different passphrases for higher security. This can be done using `-D` or `--database` option.

#### Creating databases

```bash
passpie -D ~/credentials/personal init
passpie -D ~/credentials/work init
passpie -D ~/credentials/junk init
```

#### Adding passwords to specific database

```bash
passpie -D ~/credentials/personal add johnd@github.com --random
passpie -D ~/credentials/work add john.doe@example.com --random
passpie -D ~/credentials/junk add fake@example.com --random
```

#### Listing passwords from specific database

```bash
$ passpie -D ~/databases/junk
===========  =======  ==========  =========
Name         Login    Password    Comment
===========  =======  ==========  =========
example.com  fake     *****
===========  =======  ==========  =========
```

### Passpie completion

You can activate passpie completion for `bash` or `zsh` shells

> Check the generated script with `passpie complete {shell_name}`.

#### bash

Add this line to your .bash_profile or .bashrc

```
if which passpie > /dev/null; then eval "$(passpie complete bash)"; fi
```

#### zsh

Add this line to your .zshrc or .zpreztorc

```
if which passpie > /dev/null; then eval "$(passpie complete zsh)"; fi
```

### Configuring passpie with `.passpierc`

You can override default passpie configuration with a `.passpierc` file on your home directory. Passpie configuration files must be written as a valid [yaml](http://yaml.org/) file.

#### Example `.passpierc`:

```yaml
path: /Users/john.doe/.passpie
short_commands: true
genpass_length: 32
genpass_symbols: "_-#|+= "
table_format: fancy_grid
headers:
  - name
  - login
  - password
  - comment
colors:
  login: green
  name: yellow
  password: cyan
```

#### Global configuration

##### `path =`

**default** ~/.passpie

Path to passpie database

##### `short_commands = (true | false)`

**default** false

Use passpie commands with short aliases. Like `passpie a` for `passpie add`

##### `genpass_length =`

**default:** `32`

Length of randomly generated passwords with option `--random`

##### `genpass_symbols =`

**default:** `"_-#|+= "`

Symbols used on random password generation

##### `table_format = (fancy_grid | rst | simple | orgtbl | pipe | grid | plain | latex)`

**default:** `fancy_grid`

Table format when listing credentials

##### `headers = (name | login | password | comment | fullname)`

**default:**

```
headers:
  - name
  - login
  - password
  - comment
```

##### `colors = (green | red | blue | white | cyan | magenta | yellow)`

**default:**

```
colors:
  name: yellow
  login: green
```

## Under The Hood

### Encryption

Encryption is done with **GnuGPG** using [AES256](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard). Take a look at [passpie.crypt](https://github.com/marcwebbie/passpie/blob/master/passpie/crypt.py) module to know more.

### Database Path

The default database path is at `~/.passpie`. If you want to change the database path, add `--database` option to passpie. Together with `init` you can create arbitrary databases.

```bash
passpie --database "/path/to/another/database/" init
```

### Database structure

Passpie database is structured in a directory hierachy. Every
credential is a `.pass` file inside a directory named after a credential group.

An empty database would look like this:

```bash
passpie --database /tmp/passpie init

tree /tmp/passpie -la
# /tmp/passpie
# └── .keys
```

After adding a new credential the database would look like this:

```bash
passpie --database /tmp/passpie add octocat@github.com
# Password: **********

tree /tmp/passpie -la
# /tmp/passpie
# ├── .keys
# └── github.com
#     └── octocat.pass
```

If we add more credentials to group github.com. Directory structure would be:

```bash
passpie --database /tmp/passpie add octocat2@github.com
# Password: **********

tree /tmp/passpie -la
# /tmp/passpie
# ├── .keys
# └── github
#     └── octocat.pass
#     └── octocat2.pass
```

## Contributing

Feel free to comment, open a bug report or ask for new features on Passpie [issues](https://github.com/marcwebbie/passpie/issues) page or over [Twitter](https://twitter.com/marcwebbie).

If you want to contributing with code:

- Fork the repository [https://github.com/marcwebbie/passpie/fork](https://github.com/marcwebbie/passpie/fork)
- Make sure to add tests
- Create a pull request
- [optional] Read the [Makefile](https://github.com/marcwebbie/passpie/blob/master/Makefile)


## Common issues

### `TypeError: init() got an unexpected keyword argument 'binary'`

You probably have the `python-gnupg` package installed. Passpie depends on [isislovecruft](https://github.com/isislovecruft) fork of [python-gnupg](https://github.com/isislovecruft/python-gnupg)

To fix:

```
pip uninstall python-gnupg
pip install -U passpie
```

### `'GPG not installed. https://www.gnupg.org/'`

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

### `xclip or xsel not installed`

You don't have copy to clipboard support by default on some linux distributions.

Ubuntu:

```
sudo apt-get install xclip
```

## License ([MIT License](http://choosealicense.com/licenses/mit/))

The MIT License (MIT)

Copyright (c) 2014-2015 Marc Webbie, <http://github.com/marcwebbie>

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
