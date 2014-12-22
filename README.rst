##################################################
Pysswords: Manage your passwords from the terminal
##################################################

.. image:: https://travis-ci.org/marcwebbie/pysswords.svg
   :target: https://travis-ci.org/marcwebbie/pysswords
   :alt: Build
.. image:: https://coveralls.io/repos/marcwebbie/pysswords/badge.png
   :target: https://coveralls.io/r/marcwebbie/pysswords
   :alt: Test Coverage
.. image:: https://landscape.io/github/marcwebbie/pysswords/master/landscape.svg
   :target: https://landscape.io/github/marcwebbie/pysswords/master
   :alt: Code Health

`Pysswords <https://github.com/marcwebbie/pysswords>`_ lets you manage your login credentials from the terminal. Password files are saved into GPG encrypted files into the `database path`_. Only with the passphrase used to create the pyssword database you can decrypt password file. If you want to know more about how pysswords works, check the `Under the Hood`_ section.


************
Installation
************

Make sure you have `GnuGPG <https://www.gnupg.org/>`_ installed.

.. code-block:: bash

    pip install pysswords


**********
Quickstart
**********

Check the implemented features on the `Features`_ section.

.. code-block:: bash

    # create a new credentials database. Option: `-I` or `--init`
    pysswords --init

    # add new credentials. Option: `-a` or `--add`
    pysswords -a

    # get credential with name "github". Option: `-g` or `--get`
    pysswords -g github

    # delete credential with name "github". Option: `-d` or `--delete`
    pysswords -d github

    # search credentials with query "github". Option: `-s` or `--search`
    pysswords -s github

    # copy password from credential named "github" into clipboard. Option: `-c` or `--clipboard`
    pysswords -c github

    # print all credentials as a table with hidden passwords
    pysswords

    # print all credentials as a table shows password in plain text. Option: `--show-password`
    pysswords --show-password



************
Contributing
************

+ fork the repository `<https://github.com/marcwebbie/pysswords/fork>`_
+ write your tests on `tests/test.py`
+ if everything is OK. push your changes and make a pull request. ;)


******************
Development status
******************

.. image:: https://pypip.in/version/pysswords/badge.svg
    :target: https://pypi.python.org/pypi/pysswords/
    :alt: Latest Version
.. image:: https://pypip.in/download/passwords/badge.svg
   :target: https://pypi.python.org/pypi/pysswords
   :alt: Downloads
.. image:: https://pypip.in/py_versions/pysswords/badge.svg
   :target: https://pypi.python.org/pypi/pysswords/
   :alt: Supported Python versions


********
Features
********

In order of priority [#]_:

- **[ ]** Database module
- **[ ]** Encryption module
- **[ ]** Console interface
- **[ ]** Group credentials with a password for each group

.. [#] **[ ]** not yet implemented feature, **[x]** implemented feature

**************
Under The Hood
**************

Encryption
==========

Encryption is done using GPG. Take a look at `pysswords.crypt <https://github.com/marcwebbie/pysswords/blob/master/pysswords/crypt.py>`_ module to know more.

Database path
===============

The default database path is at `~/.pysswords`. If you want to change the database path at database creation pass the --database option to pysswords

.. code-block:: bash

    pysswords --init --database "/path/to/database/"

Database structure
==================

Pysswords database is structured in a directory hierachy. Every credential is a directory named with credential name inside the database path.

An empty database would look like this:

.. code-block:: bash

   pysswords --database /tmp/pysswords --init

   tree /tmp/pysswords -la
   # /tmp/pysswords
   # └── .gnupg
   #     ├── pubring.gpg
   #     ├── random_seed
   #     ├── secring.gpg
   #     └── trustdb.gpg

After adding a new credential the database would look like this:

.. code-block:: bash

    pysswords --database /tmp/pysswords -a
    #Name: github
    #Login: octocat
    #Password: **********
    #Comments [optional]:

    tree /tmp/pysswords -la
    #/tmp/pysswords
    #├── .gnupg
    #│   ├── pubring.gpg
    #│   ├── random_seed
    #│   ├── secring.gpg
    #│   └── trustdb.gpg
    #└── github
    #    ├── comments
    #    ├── login
    #    └── password



******************************************************************
License (`MIT License <http://choosealicense.com/licenses/mit/>`_)
******************************************************************


The MIT License (MIT)

Copyright (c) 2014 Marc Webbie, http://github.com/marcwebbie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
