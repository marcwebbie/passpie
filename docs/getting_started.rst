Getting Started
*******************************************************

Installation
------------

Requirements
++++++++++++

- `GnuPG <https://www.gnupg.org/download/index.html>`_: The GNU Privacy Guard
- [Linux] `xclip <http://sourceforge.net/projects/xclip/>`_ or `xsel <https://apps.ubuntu.com/cat/applications/xsel/>`_: For copy to clipboard support

Stable
++++++

::

    pip install passpie

Or if you are on a mac, install via `Homebrew <http://brew.sh>`_::

    brew install passpie

Development versison
++++++++++++++++++++

::

    pip install -U https://github.com/marcwebbie/passpie/tarball/master


Fullnames queries
-----------------

Passpie queried using ``fullname`` syntax. fullname syntax
handles login and name for credentials in one go for faster adding and
querying of credentials.

Structure of a fullname
+++++++++++++++++++++++

Fullnames are composed of ``login``\ @\ ``name``. Login is optional. Fullnames have 3 possible formats:

- ``login@name``
- ``@name``
- ``name``

For example adding credentials using ``@name`` syntax::

    passpie add @banks/mybank --password 1234
    passpie add @banks/myotherbank --password 5678

Listing credentials::

    $ passpie
    ╒═══════════════════╤═════════╤════════════╤═══════════╕
    │ Name              │ Login   │ Password   │ Comment   │
    ╞═══════════════════╪═════════╪════════════╪═══════════╡
    │ banks/mybank      │         │ *****      │           │
    ├───────────────────┼─────────┼────────────┼───────────┤
    │ banks/myotherbank │         │ *****      │           │
    ╘═══════════════════╧═════════╧════════════╧═══════════╛

Since ``login`` is optional. You can query credentials using only name
syntax, for example to update credential with name ``banks/mybank``::

    passpie update @banks/mybank --random

Or even better, without using the ``@`` notation::

    passpie update banks/mybank --random


Configuration
-------------

For debugging, it might be useful to check actual passpie configuration for your commands::

  passpie config

Printing specific config::

  passpie config RANDOM_PASSWORD

Setting a new value in local config::

  passpie config RANDOM_PASSWORD true

Setting a new value in global config::

  passpie config --global RANDOM_PASSWORD true

 Configuration can also be overriden by environment_variables::

   export PASSPIE_PUSH=origin/master
   export PASSPIE_RANDOM_PASSWORD=true
   export PASSPIE_RECIPIENT=jonh.doe@example.com

..

.. note::

   If you have pygments installed, to have colored output on the config::

     passpie config | pygmentize -l YAML


Random Passwords
----------------

Random password pattern can be set via ``PASSWORD_PATTERN`` config.

.. code-block:: bash

    # Adding credential with random password using config pattern
    passpie add john.doe@example.com

    # Adding credential with random password overriding pattern
    passpie add john.doe@example.com --pattern '[0-9]{5}[a-z]{5}'

    # Updating credential with random password pattern
    passpie update john.doe@example.com --pattern "[0-9\#\$\%\w\ ]{32}"

    # Adding credential with random password and copy generated password to clipboard
    passpie add john.doe@example.com --copy --pattern '[0-9]{5}[a-z]{5}'


Searching
---------

.. code-block:: bash

    # search credentials by string "exam"
    passpie search exam

    # search credentials using regular expressions
    passpie search '[fF]oo|bar'


Clipboard
---------

Copying passwords to clipboard
++++++++++++++++++++++++++++++

.. code-block:: bash

    # Copying password to clipboard using ``login@name``
    passpie copy foo@example.com

    # Copying password using only ``name``
    # only one credential with name ``example.com`` should exist
    passpie copy example.com

Copying passwords to clipboard with clear timeout
+++++++++++++++++++++++++++++++++++++++++++++++++

To clear the clipboard automatically after a few seconds run copy with ``timeout`` option

.. code-block:: bash

    # Clear the clipbard after 5 seconds
    passpie copy -t 5 foo@example.com


Add or update and copy
+++++++++++++++++++++++++++

.. code-block:: bash

    # Adding credential with random password pattern
    passpie add john.doe@example.com --random --pattern '[0-9]{5}[a-z]{5}'

    # Updating credential with random password pattern
    passpie update john.doe@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"

    # Adding credential with random password and copy generated password to clipboard
    passpie add john.doe@example.com --copy --random --pattern '[0-9]{5}[a-z]{5}'

Version Control
---------------

Initializing a database with git
++++++++++++++++++++++++++++++++

By default all databases are initialized with a git repository if git is installed:

.. code-block:: bash

    passpie init

Avoiding git initialization
+++++++++++++++++++++++++++

.. code-block:: bash

    passpie init --no-git

or set ``GIT`` to ``false`` in the config

Multiple Databases
------------------

Sometimes it is useful to have multiple databases with different
passphrases for higher security. This can be done using ``-D`` or
``--database`` option.

Creating databases
++++++++++++++++++

.. code-block:: bash

    passpie -D ~/credentials/personal init
    passpie -D ~/credentials/work init
    passpie -D ~/credentials/junk init

Adding passwords to specific database
+++++++++++++++++++++++++++++++++++++

.. code-block:: bash

    passpie -D ~/credentials/personal add johnd@github.com --random
    passpie -D ~/credentials/work add john.doe@example.com --random
    passpie -D ~/credentials/junk add fake@example.com --random

Listing passwords from specific database
++++++++++++++++++++++++++++++++++++++++

.. code-block:: bash

    passpie -D ~/databases/junk


Remote databases with git
-------------------------

.. code-block:: bash

    # Listing credentials from a remote database
    passpie -D https://foo@example.com/user/repo.git

    # Adding credentials to a remote database and autopushing changes
    passpie -D https://foo@example.com/user/repo.git --autopush "origin/master" add foo+nouveau@example.com

    # Exporting environment variables
    export PASSPIE_DATABASE=https://foo@example.com/user/repo.git
    export PASSPIE_PUSH=origin/master

    # List remote credentials
    passpie

    # Copy remote `foo@example.com` password
    passpie copy foo@example.com

    # Add credential with random password directly to remote
    passpie add foo+nouveau@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"
    passpie add foo+nouveau@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"

..

.. note::

   There is an example database on: https://github.com/marcwebbie/passpiedb

Grouping Credentials
--------------------

Adding credentials with the same name, groups them accordingly::

    # add some credentials
    passpie add jonh@example.com --comment "Jonh main mail" --random
    passpie add doe@example.com --comment "No comment" --random

Listing credentials::

    $ passpie
    ╒═════════════╤═════════╤════════════╤════════════════╕
    │ Name        │ Login   │ Password   │ Comment        │
    ╞═════════════╪═════════╪════════════╪════════════════╡
    │ example.com │ doe     │ *****      │ No comment     │
    ├─────────────┼─────────┼────────────┼────────────────┤
    │ example.com │ jonh    │ *****      │ Jonh main mail │
    ╘═════════════╧═════════╧════════════╧════════════════╛

Subgroups
+++++++++

Write names separated by slashes and passpie will form subgroups of credentials by name::

    passpie add foo@opensource/github.com --random
    passpie add foo@opensource/python.org --random
    passpie add foo@opensource/bitbucket.org --random
    passpie add foo@opensource/npm.org --random

    # More nesting
    passpie add @cards/credit/mastercard --password "1111 2222 3333 4444"
    passpie add @cards/credit/mastercard/cvv --password "123"
    passpie add @cards/credit/visa --password "1111 2222 3333 4444"
    passpie add @cards/credit/visa/cvv --password "456"
    passpie add @cards/credit/amex --password "1111 2222 3333 4444"
    passpie add @cards/credit/amex/cvv --password "789"

Listing credentials::

    $ passpie
    ╒═════════════════════════════╤═════════╤════════════╤═══════════╕
    │ Name                        │ Login   │ Password   │ Comment   │
    ╞═════════════════════════════╪═════════╪════════════╪═══════════╡
    │ cards/credit/amex           │         │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ cards/credit/amex/cvv       │         │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ cards/credit/mastercard     │         │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ cards/credit/mastercard/cvv │         │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ cards/credit/visa           │         │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ cards/credit/visa/cvv       │         │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ opensource/bitbucket.org    │ foo     │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ opensource/github.com       │ foo     │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ opensource/npm.org          │ foo     │ *****      │           │
    ├─────────────────────────────┼─────────┼────────────┼───────────┤
    │ opensource/python.org       │ foo     │ *****      │           │
    ╘═════════════════════════════╧═════════╧════════════╧═══════════╛


Shell Completion
----------------

You can activate passpie completion for ``bash``, ``zsh`` or ``fish`` shells

> Check the generated script with ``passpie complete {shell_name}``.

``bash``
++++++++

Add this line to your ``.bash_profile`` or ``.bashrc``

::

   if which passpie > /dev/null; then eval "$(passpie complete bash)"; fi

``zsh``
+++++++

Add this line to your ``.zshrc`` or ``.zpreztorc``

::

   if which passpie > /dev/null; then eval "$(passpie complete zsh)"; fi

``fish``
++++++++

Add this line to your ``~/.config/fish/config.fish``

::

   if which passpie > /dev/null; passpie complete fish | source ; end


Importing and Exporting
-----------------------

Exporting credentials
+++++++++++++++++++++

::

    passpie export passwords.db

.. warning::

   Passpie exports databases credentials in plain text


Importing credentials
+++++++++++++++++++++

Passpie importers use a list of importers to to try and handle the paswords file passed.

Available importers:

| ★ Passpie (default)
| ★ Keepass (CSV)
| ★ CSV general importer

Importing default credentials exported using passpie::

  passpie import passwords.txt


CSV configurable importer
~~~~~~~~~~~~~~~~~~~~~~~~~

Importing from a CSV file. Specify ``--cols`` option to map columns to credential attributes.

**Keepass** exported credentials as ``keepass.csv``::

  "Group","Title","Username","Password","URL","Notes"
  "Root","Some Title","john.doe","secret","example.com","Some comments"
  "Root","Another title","foo.bar","p4ssword","example.org",""

Import credentials with::

  passpie import --cols ",,login,password,name,comment" keepass.csv


**Lastpass** exported credentials as ``lastpass.csv``::

  "Group","Title","Username","Password","URL","Notes"
  "Root","Some Title","john.doe","secret","example.com","Some comments"
  "Root","Another title","foo.bar","p4ssword","example.org",""

Import with::

  passpie import --cols "name,login,password,,comment" lastpass.csv


GnuPG keys
----------

By default *Passpie* creates a GnuPG `keyring <https://en.wikipedia.org/wiki/Keyring_(cryptography)>`_ for each initialized database.
This keyring will be used to encryt/decrypt credentials from database.

To prevent this behavior, set the a recipient when initializing the database::

  passpie init --recipient foo@example.com

Or for an already initialized database, set the recipient to the config file:

.. code-block:: yaml

   recipient: foo@example.com


Reseting and Purging Databases
------------------------------

::

    # Delete all credentials from database
    passpie remove --all

    # Redefine passphrase and reencrypt all credentials from database
    passpie reset

Debugging
---------

::

    # get help on commands
    passpie --help

    # activating verbose output
    passpie -v

    # activating even more verbose output
    passpie -vv
