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


## Learn more

- [Diving into *fullname* syntax](https://github.com/marcwebbie/passpie/blob/master/docs/fullname.md)
- [Configuration](https://github.com/marcwebbie/passpie/blob/master/docs/configuration.md)
- [Grouping Credentials](https://github.com/marcwebbie/passpie/blob/master/docs/grouping.md)
- [Multiple Databases](https://github.com/marcwebbie/passpie/blob/master/docs/multiple_databases.md)
- [Syncing Credentials](https://github.com/marcwebbie/passpie/blob/master/docs/syncing.md)
- [Version Control With Git](https://github.com/marcwebbie/passpie/blob/master/docs/syncing.md)
- [Exporting Credentials](#)
- [Importing Credentials](https://github.com/marcwebbie/passpie/blob/master/docs/importing.md)



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
