Pysswords: Manage your passwords from the terminal
==================================================

[Pysswords](https://marcwebbie.github.io/pysswords) lets you manage
your login credentials from the terminal. Password files are saved into
[GnuGPG](http://en.wikipedia.org/wiki/GNU_Privacy_Guard) encrypted files
into the Database Path\_. Only with the passphrase used to create the
pyssword database you can decrypt password files. If you want to know
more about how pysswords works internally, check the Under the Hood\_
section.

![Pysswords console interface](https://github.com/marcwebbie/pysswords/raw/master/images/pysswords2.png)

------------------------------------------------------------------------


Main Features
-------------

+ `☑` Console interface
+ `☑` Manage multiple databases
+ `☑` Add, edit, remove credentials
+ `☑` Copy passwords to clipboard
+ `☑` List credentials as a table
+ `☑` Colored output
+ `☑` Search credentials by name, login or comments
+ `☑` Search with regular expression
+ `☑` Bulk update/remove credentials
+ `☑` Select credentials by fullname syntax
+ `☑` Grouping credentials
+ `☑` Exporting Pysswords database
+ `☑` Importing Pysswords database
+ `☐` Undo/Redo modifications to the database
+ `☐` Importing credentials from other applications

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

# get credential "example". Option: `-g` or `--get`
pysswords -g example

# remove credential "example". Option: `-r` or `--remove`
pysswords -r example

# edit credential "example". Option: `-u` or `--update`
pysswords -u example

# search credentials with the query "octocat". Option: `-s` or `--search`
pysswords -s octocat

# search credentials with the regular expression "example\.com|org".
pysswords -s example\.com|org

# copy password from credential "example" into clipboard. Option: `-c` or `--clipboard`
# this option have to be used with --get|-g option
pysswords -c -g example

# print all credentials as a table with hidden passwords
pysswords

# print all credentials and show passwords in plain text. Option: `-P` or `--show-password`
pysswords -P

# delete database and remove all credentials
pysswords --clean

# export database to a pysswords database file called pysswords.db
pysswords --export pysswords.db

# import database from pysswords database file called pysswords.db
pysswords --import pysswords.db

# specify other pysswords database. Option `-D` or `--database`
pysswords -D /path/to/other/database

# shows help. Option `-h` or `--help`
pysswords --help

# shows version. Option `--version`
pysswords --version
```


### Grouping

Pysswords credentials can have multiple names which groups credentials with the same name together:

```
pysswords -a
Name: example.com
Login: john
Password: **********
Comment: No comment
```

```
pysswords -a
Name: example.com
Login: doe
Password: **********
Comment:
```

###### Output

```

| Name        | Login   | Password   | Comment    |
|-------------+---------+------------+------------|
| example.com | doe     | ***        |            |
| example.com | john    | ***        | No comment |

```

### Fullname syntax

You can select grouped credentials by using fullname syntax `login@name`:

```
pysswords -g doe@example.com
```

###### Output

```

| Name        | Login   | Password   | Comment   |
|-------------+---------+------------+-----------|
| example.com | doe     | ***        |           |

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
credential is a `.pyssword` file inside a directory named after a credential group.

An empty database would look like this:

```bash
pysswords --database /tmp/pysswords --init

tree /tmp/pysswords -la
# /tmp/pysswords
# └── .keys
#     ├── pubring.gpg
#     ├── random_seed
#     ├── secring.gpg
#     └── trustdb.gpg
```

After adding a new credential the database would look like this:

```bash
pysswords --database /tmp/pysswords -a
# Name: github.com
# Login: octocat
# Password: **********
# Comments:

tree /tmp/pysswords -la
# /tmp/pysswords
# ├── .keys
# │   ├── pubring.gpg
# │   ├── random_seed
# │   ├── secring.gpg
# │   └── trustdb.gpg
# └── github.com
#     └── octocat.pyssword
```

If we add more credentials to group github.com. Directory structure would be:

```bash
pysswords --database /tmp/pysswords -a
# Name: github.com
# Login: octocat2
# Password: **********
# Comments:

tree /tmp/pysswords -la
# /tmp/pysswords
# ├── .keys
# │   ├── pubring.gpg
# │   ├── random_seed
# │   ├── secring.gpg
# │   └── trustdb.gpg
# └── github
#     └── octocat.pyssword
#     └── example.pyssword
```


Contributing
------------

- Fork the repository [https://github.com/marcwebbie/pysswords/fork](https://github.com/marcwebbie/pysswords/fork)
- Read the [Makefile](https://github.com/marcwebbie/pysswords/blob/master/Makefile)
- Write your tests on `tests/test.py`
- If everything is OK. push your changes and make a pull request. ;)


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
