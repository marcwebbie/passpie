Getting Started
*******************************************************

Installing
----------

Requirements
++++++++++++

- ``GnuPG``
- ``xclip`` or ``xsel`` - [Linux] For copy to clipboard support

::

    pip install passpie

Or if you are on a mac, install via `Homebrew <http://brew.sh>`_::

    brew install passpie

Development version::

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
    =================  =======  ==========  =========
    Name               Login    Password    Comment
    =================  =======  ==========  =========
    banks/mybank                *****
    banks/myotherbank           *****
    =================  =======  ==========  =========

Since ``login`` is optional. You can query credentials using only name
syntax, for example to update credential with name ``banks/mybank``::

    passpie update @banks/mybank --random

Or even better, without using the ``@`` notation::

    passpie update banks/mybank --random


Random Passwords
----------------

Random password pattern can be set via ``genpass_pattern`` config.

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


Add or update and copy
+++++++++++++++++++++++++++

.. code-block:: bash

    # Adding credential with random password pattern
    passpie add john.doe@example.com --random --pattern '[0-9]{5}[a-z]{5}'

    # Updating credential with random password pattern
    passpie update john.doe@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"

    # Adding credential with random password and copy generated password to clipboard
    passpie add john.doe@example.com --copy --random --pattern '[0-9]{5}[a-z]{5}'

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

..

Or using `configuration <#>`_

Logging
+++++++

To log changes to the database, use passpie command ``log``

.. code-block:: bash

    passpie log

outputs:

.. code:: text

    [13] Updated foo@bar
    [12] Updated foo@bar
    [11] Reset database
    [10] Removed foozy@bar
    [9] Updated hello@world
    [8] Added hello@world
    [7] Added foozy@bar
    [6] Updated test@github
    [5] Added foozy@bazzy
    [4] Updated test@github
    [3] Added foo@bar
    [2] Added spam@egg
    [1] Added test@github
    [0] Initialized database

Resetting
+++++++++

If you want to go back to a previous version of the database history:
``passpie --reset-to N`` where N is the index of the change.

.. code-block:: bash

    passpie log --reset-to 5

..

    *Attention*: this is an operation that destroys data. Use it with
    caution. It is equivalent to do ``git reset --hard HEAD~N``


Remote databases
++++++++++++++++

.. code-block:: bash

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

Grouping Credentials
--------------------

Passpie credentials handles multiple logins for each name which groups
credentials by name:

::

    # add some credentials
    passpie add jonh@example.com --comment "Jonh main mail" --random
    passpie add doe@example.com --comment "No comment" --random

Listing credentials:

::

    $ passpie

Subgroups
+++++++++

Fullname syntax supports subgrouping of credentials by name

::

    passpie add foo@opensource/github.com --random
    passpie add foo@opensource/python.org --random
    passpie add foo@opensource/bitbucket.org --random
    passpie add foo@opensource/npm.org --random

Listing credentials:

::

    $ passpie
    ========================  =======  ==========  =========
    Name                      Login    Password    Comment
    ========================  =======  ==========  =========
    opensource/bitbucket.org  foo      *****
    opensource/github.com     foo      *****
    opensource/npm.org        foo      *****
    opensource/python.org     foo      *****
    ========================  =======  ==========  =========

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

   if which passpie > /dev/null; then eval "$(passpie complete zsh)"; fi


Importing and Exporting
-----------------------

Exporting a passpie database
++++++++++++++++++++++++++++

::

    passpie export passpie.db

..

    ❗ Passpie exports databases credentials in plain text


Importing a passpie database
++++++++++++++++++++++++++++

::

    passpie import passpie.db

Database status
---------------

To have a status report on the database run:

::

    passpie status

Available checkers are:

- repeated passwords
- old passwords

GnuPG keys
----------

Reseting and Purging Databases
------------------------------

::

    # Delete all credentials from database
    passpie purge

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
