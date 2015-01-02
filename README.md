Pysswords: Manage your passwords from the terminal
==================================================

[Pysswords](https://marcwebbie.github.io/pysswords) lets you manage
your login credentials from the terminal. Password files are saved into
[GnuGPG](http://en.wikipedia.org/wiki/GNU_Privacy_Guard) encrypted files
into the Database Path\_. Only with the passphrase used to create the
pyssword database you can decrypt password files. If you want to know
more about how pysswords works internally, check the Under the Hood\_
section.

![Pysswords console interface](https://github.com/marcwebbie/pysswords/raw/master/images/pysswords.png)

------------------------------------------------------------------------


Main Features
-------------

+ `☑` Console interface
+ `☑` Manage multiple databases
+ `☑` Add, edit, remove credentials
+ `☑` Copy passwords to clipboard
+ `☑` Search credentials by name, login or comments
+ `☑` List credentials as a table
+ `☑` Colored output
+ `☐` Search with regular expression
+ `☐` Importing credentials from other applications
+ `☐` Undo/Redo modifications to the database
+ `☐` Pysswords emacs mode

> `☑` implemented feature, `☐` not implemented feature.


Installation
------------

### Stable version ![pypi version](https://img.shields.io/pypi/v/pysswords.svg)

Make sure you have [GPG](https://www.gnupg.org/) and [pip](http://pip.readthedocs.org/en/latest/installing.html) installed.

```bash
pip install pysswords
```

### Development version [![Test Coverage](https://img.shields.io/coveralls/marcwebbie/pysswords.svg)](https://coveralls.io/r/marcwebbie/pysswords) [![Code Health](https://landscape.io/github/marcwebbie/pysswords/master/landscape.svg)](https://landscape.io/github/marcwebbie/pysswords/master).

Mac/linux | Windows
----------|---------
[![Build](https://travis-ci.org/marcwebbie/pysswords.svg)](https://travis-ci.org/marcwebbie/pysswords) | [![Build on windows](https://ci.appveyor.com/api/projects/status/5b7p1vo3y9x3y35t?svg=true)](https://ci.appveyor.com/project/marcwebbie/pysswords)

The **latest development version** can be installed directly from GitHub:

```bash
# Universal
$ pip install --upgrade https://github.com/marcwebbie/pysswords/tarball/master
```


Quickstart
----------

```bash
# create a new credentials database. Option: `-I` or `--init`
pysswords --init

# add new credentials. Option: `-a` or `--add`
pysswords -a

# get credential "github". Option: `-g` or `--get`
pysswords -g github

# remove credential "github". Option: `-r` or `--remove`
pysswords -d github

# edit credential "github". Option: `-e` or `--edit`
pysswords -e github

# search credentials with query "octocat". Option: `-s` or `--search`
pysswords -s octocat

# copy password from credential "github" into clipboard. Option: `-c` or `--clipboard`
# this option have to be used with --get|-g option
pysswords -c -g github

# print all credentials as a table with hidden passwords
pysswords

# print all credentials and show passwords in plain text. Option: `--show-password`
pysswords --show-password

# shows help. Option `-h` or `--help`
pysswords --help
```


Under The Hood
--------------

### Encryption

Encryption is done with **GnuGPG** using [AES256](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard). Take a look at [pysswords.crypt](https://github.com/marcwebbie/pysswords/blob/master/pysswords/crypt.py) module to know more.

### Database Path

The default database path is at `~/.pysswords`. If you want to change the database path, add `--database` option to pysswords together with `--init`.

```bash
pysswords --init --database "/path/to/database/"
```

### Database structure

Pysswords database is structured in a directory hierachy. Every
credential is a directory named with credential name inside the database
path.

An empty database would look like this:

```bash
pysswords --database /tmp/pysswords --init

tree /tmp/pysswords -la
# /tmp/pysswords
# └── .gnupg
#     ├── pubring.gpg
#     ├── random_seed
#     ├── secring.gpg
#     └── trustdb.gpg
```

After adding a new credential the database would look like this:

```bash
pysswords --database /tmp/pysswords -a
# Name: github
# Login: octocat
# Password: **********
# Comments [optional]:

tree /tmp/pysswords -la
# /tmp/pysswords
# ├── .gnupg
# │   ├── pubring.gpg
# │   ├── random_seed
# │   ├── secring.gpg
# │   └── trustdb.gpg
# └── github
#     ├── comments
#     ├── login
#     └── password
```


Contributing
------------

-   Fork the repository [https://github.com/marcwebbie/pysswords/fork](https://github.com/marcwebbie/pysswords/fork)
-   Write your tests on `tests/test.py`
-   If everything is OK. push your changes and make a pull request. ;)


License ([MIT License](http://choosealicense.com/licenses/mit/))
----------------------------------------------------------------

The MIT License (MIT)

Copyright (c) 2014 Marc Webbie, <http://github.com/marcwebbie>

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
