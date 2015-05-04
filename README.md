# Passpie: Manage passwords from the terminal

[Passpie](https://marcwebbie.github.io/passpie) lets you manage your login credentials from the terminal with a coloroful/configurable cli interface. Password files are saved into [GnuPG](http://en.wikipedia.org/wiki/GNU_Privacy_Guard) encrypted files into the Database Path. Use your master passphrase to decrypt password files or copy passwords to clipboard.

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
+ [x] Configuration from file. `~/.passpie`
+ [x] Change passphrase and re-encrypt database
+ [x] Export Passpie database to plain text file
+ [x] Import plain text Passpie database
+ [ ] Import credentials from [1Password](https://agilebits.com/onepassword)
+ [x] Import credentials from [Pysswords](https://github.com/marcwebbie/pysswords)
+ [x] Randomly generated credential passwords
+ [x] Configurable random password generation
+ [x] Generate database status report
+ [ ] Undo/Redo updates to the database
+ [ ] Bulk update/remove credentials


## Installation

### Stable version

Make sure you have [GPG](https://www.gnupg.org/) and [pip](http://pip.readthedocs.org/en/latest/installing.html) installed:

```bash
pip install passpie
```

### Development version

The **latest development version** can be installed directly from GitHub:

```bash
pip install --upgrade https://github.com/marcwebbie/passpie/tarball/master
```

## Quickstart

```bash
# create a new credentials database.
passpie init

# add new credentials.
passpie add foo@example.com
passpie add bar@example.com

# add credential with random password
passpie add spam@egg.local --random

# edit credential "foo@example.com".
passpie update foo@example.com

# copy password from credential "foo@example.com" into system clipboard.
passpie copy foo@example.com

# search credentials by string "exam".
passpie search exam

# search credentials using regular expressions.
passpie search 'foo|bar'

# remove credential "foo@example.com".
passpie remove foo@example.com

# check database status
passpie status

# print all credentials as a table with hidden passwords
passpie

# specify other Passpie database. Option `-D` or `--database`
passpie -D /path/to/other/database

# shows help. Option `--help`
passpie --help

# shows version. Option `--version`
passpie --version
```

## Usage

```bash
Usage: passpie [OPTIONS] COMMAND [ARGS]...

Options:
  -D, --database PATH  Alternative database path
  --version            Show the version and exit.
  --help               Show this message and exit.

Commands:
  add     Add new credential
  copy    Copy credential password to clipboard
  export  Export credentials in plain text
  import  Import credentials from path
  init    Initialize new passpie database
  remove  Remove credential
  reset   Renew passpie database and re-encrypt...
  search  Search credentials by regular expressions
  status  Diagnose database for improvements
  update  Update credential
```

## Tutorials

### 1. Diving into *fullname* syntax

Passpie fullname syntax handles login and name for credentials in one go for faster adding and querying.

#### Structure of a fullname

`login`@`name`. Login is optional,  when adding new credentials without login, login will be replaced by a `_` character:

```bash
passpie add @banks/mybank --password 1234
passpie add @banks/myotherbank --password 5678
```

Listing the database would show:

```bash
$ passpie
=================  =======  ==========  =========
Name               Login    Password    Comment
=================  =======  ==========  =========
banks/mybank       _        *****
banks/myotherbank  _        *****
=================  =======  ==========  =========
```

### 2. Syncing your database

#### Dropbox

Assuming you have passpie database on the default path `~/.passpie` and a Dropbox shared directory on path `~/Dropbox`

##### 1. Move your Passpie database inside your Dropbox directory:

```bash
mv ~/.passpie ~/Dropbox/passpie
```

##### 2. create a symbolic link to your shared `passpie` directory on the default path.

```bash
ln -s ~/Dropbox/passpie ~/.passpie
```

#### Google Drive

Assuming you have passpie database on the default path `~/.passpie` and a Google Drive shared directory on path `~/GoogleDrive`


##### 1. move your Passpie database inside your Google Drive directory

```bash
mv ~/.passpie ~/GoogleDrive/passpie
```
##### 2. create a symbolic link to your shared `passpie` directory on the default path.

```bash
ln -s ~/GoogleDrive/passpie ~.passpie
```

### 3. Exporting/Importing Passpie databases

```bash
# export database to a passpie database file called passpie.db
# Command: `export`
passpie export passpie.db

# import database from passpie database file called passpie.db
# Option: `import`
passpie import passpie.db
```

### 4. Grouping credentials by name

Passpie credentials handles multiple logins for each name which groups credentials by name:

```bash
# create john credential
passpie add jonh@example.com --comment "Jonh main mail" --random

# create doe credential
passpie add doe@example.com --comment "No comment" --random

# listing credentials
passpie
===========  =======  ==========  ===============
name         login    password    comment
===========  =======  ==========  ===============
example.com  doe      *****       No comment
example.com  jonh     *****       Jonh main email
===========  =======  ==========  ===============
```

### 5. Using multiple databases

Sometimes it is useful to have multiple databases with different passphrases for higher security. This can be done using `-D` Passpie option.

#### Creating databases on a given directory (ex: `~/databases`)

```bash
# create personal Passpie database
passpie -D ~/databases/personal_passwords init

# create work Passpie database
passpie -D ~/databases/work_passwords init

# create junk Passpie database
passpie -D ~/databases/junk_passwords init
```

#### Adding passwords to specific database

```bash
# add password to personal Passpie database
passpie -D ~/databases/personal_passwords add my@example

# add password to junk Passpie database
passpie -D ~/databases/junk_passwords add other@example
```

#### Listing passwords from specific database

```bash
# listing specific databases
passpie -D ~/databases/junk_passwords
```

### 6. Configuring passpie with `.passpierc`

You can override default passpie configuration with a `.passpierc` file on your home directory. Passpie configuration files must be written as a valid [yaml](http://yaml.org/) file.

#### Example `.passpierc`:

```yaml
path: /Users/john.doe/.passpie
short_commands: true
short_commands: true
genpass_length: 32
genpass_symbols: "_-#|+="
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

Options:

+ path: path to database. Default: `~/.passpie`
+ short_commands: Use short commands aliases as in `passpie a` for `passpie add`
+ genpass_length: number. Default: `32`
+ genpass_symbols: characters. Default: `_-#|+="`
  - true
  - false
+ headers:
  - fullname
  - name
  - login
  - password
  - comment
+ table_format:
  - rst
  - simple
  - orgtbl
  - fancy_grid
+ colors:
  - black
  - red
  - green
  - yellow
  - blue
  - magenta
  - cyan
  - white

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
- Read the [Makefile](https://github.com/marcwebbie/passpie/blob/master/Makefile)


## Common issues

### Running passpie init raises `TypeError: init() got an unexpected keyword argument 'binary'`

You probably have the `python-gnupg` package installed. Passpie depends on [isislovecruft](https://github.com/isislovecruft) fork of [python-gnupg](https://github.com/isislovecruft/python-gnupg)

To fix:

```
pip uninstall python-gnupg
pip install -U passpie
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
