:code:`passpie`: Comand-line password manager
*******************************************************

.. image:: https://raw.githubusercontent.com/marcwebbie/passpie/master/images/passpie.png
    :scale: 100%

|Version| |Build Status| |Windows Build Status| |Coverage|

Passpie is a command line tool to  manage passwords from the terminal with a colorful and configurable interface. Password files are encrypted using `GnuPG <http://en.wikipedia.org/wiki/GNU_Privacy_Guard)>`_ and saved into yaml text files. Use a master passphrase to decrypt login credentials, copy passwords to clipboard, syncronize with a git repository, check the state of your passwords, and more...

Install
========

.. code-block::

    pip install passpie

Or if you are on a mac, install via `Homebrew <http://brew.sh>`_:

.. code-block::

    brew install passpie


Quickstart
==========

.. code-block::

    passpie init
    passpie add foo@example.com --random --pattern "[0-9]{5}[a-z]{5}"
    passpie add bar@example.com --random --pattern "[0-9]{5}[a-z]{5}"
    passpie update foo@example --comment "Hello"
    passpie

Outputs:

.. code-block::

    ╒═════════════╤═════════╤════════════╤═══════════╕
    │ Name        │ Login   │ Password   │ Comment   │
    ╞═════════════╪═════════╪════════════╪═══════════╡
    │ example.com │ bar     │ *****      │           │
    ├─────────────┼─────────┼────────────┼───────────┤
    │ example.com │ foo     │ *****      │ Hello     │
    ╘═════════════╧═════════╧════════════╧═══════════╛

Features
========

| ★ Add, update, remove credentials
| ★ Manage multiple databases. Locally and remotely
| ★ Copy passwords to clipboard or to stdout
| ★ List credentials as a table with colored output
| ★ Search credentials by name, login, comments or regulax expresions
| ★ Group credentials by name
| ★ `Configuration <#configuration>`_ with ~/.passpie or .config
| ★ Version control passpie databases using git
| ★ Change passphrase and re-encrypt database
| ★ Export Passpie database to plain text file
| ★ Import credentials
| ★ Generate random passwords
| ★ Generate database status report
| ★ BASH/ZSH/FISH completion
| ★ Undo/Redo changes to the database. (requires `git <https://git-scm.com/>`_)
| ★ Set a personal gpg key recipient
| ★ Per database keyring


Tutorial
========

Initializing a database:

.. code:: bash

    passpie init

    # Initializing a database using an existing GnuPG keyring recipient
    passpie init --recipient marcwebbie@example.com

Adding credentials:

.. code:: bash

    # Adding a credential. You will be promped to enter a password
    passpie add foo@example.com

    # Adding a credential with comments
    passpie add foo+commented@example.com --comment "Commented credential"

    # Force re-adding a credential
    passpie add foo+commented@example.com --force

Grouping credentials:

.. code:: bash

    passpie add foo@opensource/github.com --random
    passpie add foo@opensource/python.org --random
    passpie add foo@opensource/bitbucket.org --random
    passpie add foo@opensource/npm.org --random

Randomizing passwords:

.. code:: bash

    # Adding credential with random password pattern
    passpie add john.doe@example.com --random --pattern '[0-9]{5}[a-z]{5}'

    # Updating credential with random password pattern
    passpie update john.doe@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"

    # Adding credential with random password and copy generated password to clipboard
    passpie add john.doe@example.com --copy --random --pattern '[0-9]{5}[a-z]{5}'

Creating multiple databases each with a different password and keys:

.. code:: bash

    # Creating multiple databases
    mkdir ~/credentials
    passpie -D ~/credentials/personal init
    passpie -D ~/credentials/work init
    passpie -D ~/credentials/junk init

    # Inserting credentials into specific databases
    passpie -D ~/credentials/personal add johnd@github.com --random
    passpie -D ~/credentials/work add john.doe@example.com --random
    passpie -D ~/credentials/junk add fake@example.com --random

Updating and removing credentials:

.. code:: bash

    # Update credential. You will be promped with changes
    passpie update foo@example.com

    # Update credential to a random password. Skip prompts
    passpie update -y --random foo@example.com

    # Remove credential
    passpie remove foo@example.com

    # Remove credential. Skip prompts
    passpie remove -y foo@example.com

Searching credentials:

.. code:: bash

    # search credentials by string "exam"
    passpie search exam

    # search credentials using regular expressions
    passpie search '[fF]oo|bar'

Version control and sync databases:

.. code:: bash

    # see the database change history
    passpie log

    # reset to a previous version of the database
    passpie --reset-to 5

    # Initialize git history on an existing database
    passpie log --init

Reseting and purging a database:

.. code:: bash

    # Delete all credentials from database
    passpie purge

    # Redefine passphrase and reencrypt all credentials from database
    passpie reset

Playing with *volatile* remote databases:

.. code:: bash

    # Listing credentials from a remote database
    passpie -D https://foo@example.com/user/repo.git

    # Adding credentials to a remote database and autopushing changes
    passpie -D https://foo@example.com/user/repo.git --autopush "origin/master" add foo+nouveau@example.com

    # Exporting environment variables
    export PASSPIE_DATABASE=https://foo@example.com/user/repo.git
    export PASSPIE_AUTOPULL=origin/master
    export PASSPIE_AUTOPUSH=origin/master

    # List remote credentials
    passpie

    # Copy remote `foo@example.com` password
    passpie copy foo@example.com

    # Add credential with random password directly to remote
    passpie add foo+nouveau@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"
    passpie add foo+nouveau@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"


Debugging:

.. code:: bash

    # get help on commands
    passpie --help

    # activating verbose output
    passpie -v

    # activating even more verbose output
    passpie -vv


Configuration
=============

Example configuration file:

.. code-block:: yaml

    # ~/.passpierc
    path: ~/.passpie
    homedir: ~/.gnupg
    autopull: null
    autopush: null
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

..

| **Name:** ``path``:
| **Default:** ``~/.passpie``
| **Description:** Path to default database.
|
| **Name:** ``homedir``:
| **Default:** ``~/.gnupg``
| **Description:** Path to default gnupg homedir.
|
| **Name:** ``autopull``:
| **Default:** ``null``
| **Description:** Automatically pull changes from remote git repository.
|
| **Name:** ``autopush``:
| **Default:** ``null``
| **Description:** Automatically pull changes from remote git repository.
|
| **Name:** ``recipient``:
| **Default:** ``null``
| **Description:** GnuPG defaul recipient. This can be a fingerprint/emai/name.
|
| **Name:** ``extension``:
| **Default:** ``.pass``
| **Description:** Password files extension
|
| **Name:** ``copy_timeout``:
| **Default:** ``0``
| **Description:** Automatically clear clipboard after n seconds
|
| **Name:** ``genpass_pattern``:
| **Default:** ``"[a-z]{5} [-_+=*&%$#]{5} [A-Z]{5}"``
| **Description:** Regex pattern for password random generation
|
| **Name:** ``table_format``:
| **Default:** ``fancy_grid``
| **Description:**
|
| **Name:** ``headers``:
| **Default:** ``[name, login, password, comments]``
| **Description:**
|
| **Name:** ``colors``:
| **Default:** ``{login: green, name: yellow}``
| **Description:** Table column colors
|
| **Name:** ``key_length``:
| **Default:** ``4096``
| **Description:** AES encryption key length
|
| **Name:** ``repo``:
| **Default:** ``true``
| **Description:** Automatically create a git repository on initialization
|
| **Name:** ``short_commands``:
| **Default:** ``false``
| **Description:**
|
| **Name:** ``status_repeated_passwords_limit``:
| **Default:** ``5``
| **Description:**


Bugs & Questions
================

You can file bugs in our github `issues tracker <https://github.com/marcwebbie/passpie/issues>`_, ask questions on our `mailing list <https://groups.google.com/d/forum/passpie>`_. Or check the `common issues sections <./docs/common_issues.md>`_ on the documentation.

| **Mailing list**: https://groups.google.com/d/forum/passpie
| **Github issues**: https://github.com/marcwebbie/passpie/issues


Contributing
============

Whether reporting bugs, discussing improvements and new ideas or writing
extensions: Contributions to Passpie are welcome! Here's how to get started:

1. Check for open issues or open a fresh issue to start a discussion around
   a feature idea or a bug
2. Fork `the repository <https://github.com/marcwebbie/passpie/>`_
   clone your fork and start making your changes
3. Write a test which shows that the bug was fixed or that the feature works
   as expected
4. Send a pull request and bug the maintainer until it gets merged and
   published ☺


Licence |License|
=================

Copyright (c) 2014-2016 Marcwebbie, <http://github.com/marcwebbie>

Full license here: `LICENSE <./LICENSE>`_


.. |Build Status| image:: http://img.shields.io/travis/marcwebbie/passpie.svg?style=flat-square
   :target: https://travis-ci.org/marcwebbie/passpie
.. |Windows Build Status| image:: https://img.shields.io/appveyor/ci/marcwebbie/passpie.svg?style=flat-square&label=windows%20build
   :target: https://ci.appveyor.com/project/marcwebbie/passpie
.. |Coverage| image:: http://img.shields.io/coveralls/marcwebbie/passpie.svg?style=flat-square
   :target: https://coveralls.io/r/marcwebbie/passpie
.. |Version| image:: http://img.shields.io/pypi/v/passpie.svg?style=flat-square&label=latest%20version
   :target: https://pypi.python.org/pypi/passpie/
.. |License| image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
