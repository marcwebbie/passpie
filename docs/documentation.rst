Documentation
*******************************************************

Usage
=========

Fullname
---------

Passpie credentials are referenced by ``fullname``. fullname syntax
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

::

    # Adding credential with random password pattern
    passpie add john.doe@example.com --random --pattern '[0-9]{5}[a-z]{5}'

    # Updating credential with random password pattern
    passpie update john.doe@example.com --random --pattern "[0-9\#\$\%\w\ ]{32}"

    # Adding credential with random password and copy generated password to clipboard
    passpie add john.doe@example.com --copy --random --pattern '[0-9]{5}[a-z]{5}'

Searching
---------

::

    # search credentials by string "exam"
    passpie search exam

    # search credentials using regular expressions
    passpie search '[fF]oo|bar'


Clipboard
---------

Copying passwords to clipboard
++++++++++++++++++++++++++++++

::

    # Copying password to clipboard using ``login@name``
    passpie copy foo@example.com

    # Copying password using only ``name``
    # only one credential with name ``example.com`` should exist
    passpie copy example.com


Add or update and copy
+++++++++++++++++++++++++++

::

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

::

    passpie -D ~/credentials/personal init
    passpie -D ~/credentials/work init
    passpie -D ~/credentials/junk init

Adding passwords to specific database
+++++++++++++++++++++++++++++++++++++

::

    passpie -D ~/credentials/personal add johnd@github.com --random
    passpie -D ~/credentials/work add john.doe@example.com --random
    passpie -D ~/credentials/junk add fake@example.com --random

Listing passwords from specific database
++++++++++++++++++++++++++++++++++++++++

::

    $ passpie -D ~/databases/junk
    ===========  =======  ==========  =========
    Name         Login    Password    Comment
    ===========  =======  ==========  =========
    example.com  fake     *****
    ===========  =======  ==========  =========

Version Control
---------------

Initializing a database with git
++++++++++++++++++++++++++++++++

By default all databases are initialized with a git repository if git is installed:

::

    passpie init

Avoiding git initialization
+++++++++++++++++++++++++++

::

    passpie init --no-git

..

Or using `configuration <./docs/configuration>`_

Logging
+++++++

To log changes to the database, use passpie command ``log``

::

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

::

    passpie log --reset-to 5

..

    *Attention*: this is an operation that destroys data. Use it with
    caution. It is equivalent to do ``git reset --hard HEAD~N``


Remote databases
++++++++++++++++

::

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

Grouping
--------

Passpie credentials handles multiple logins for each name which groups
credentials by name:

::

    # add some credentials
    passpie add jonh@example.com --comment "Jonh main mail" --random
    passpie add doe@example.com --comment "No comment" --random

Listing credentials:

::

    $ passpie
    ===========  =======  ==========  ===============
    name         login    password    comment
    ===========  =======  ==========  ===============
    example.com  doe      *****       No comment
    example.com  jonh     *****       Jonh main email
    ===========  =======  ==========  ===============

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

You can activate passpie completion for `bash` or `zsh` shells

> Check the generated script with `passpie complete {shell_name}`.

`bash`
++++++

Add this line to your `.bash_profile` or `.bashrc`

::

   if which passpie > /dev/null; then eval "$(passpie complete bash)"; fi

`zsh`
+++++

Add this line to your `.zshrc` or `.zpreztorc`

.. code:: zsh

   if which passpie > /dev/null; then eval "$(passpie complete zsh)"; fi

`fish`
++++++

Add this line to your `~/.config/fish/config.fish`

.. code:: fish

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


FAQ
===

What is a passpie database?
---------------------------

Passpie database is structured in a directory hierachy. Every credential
is a ``.pass`` file inside a directory named after a credential group.

An empty database would look like this:

.. code:: bash

    passpie --database /tmp/passpie init

    tree /tmp/passpie -la
    # /tmp/passpie
    # └── .keys

After adding a new credential the database would look like this:

.. code:: bash

    passpie --database /tmp/passpie add octocat@github.com
    # Password: **********

    tree /tmp/passpie -la
    # /tmp/passpie
    # ├── .keys
    # └── github.com
    #     └── octocat.pass

If we add more credentials to group github.com. Directory structure
would be:

.. code:: bash

    passpie --database /tmp/passpie add octocat2@github.com
    # Password: **********

    tree /tmp/passpie -la
    # /tmp/passpie
    # ├── .keys
    # └── github
    #     └── octocat.pass
    #     └── octocat2.pass

What is a fullname?
-------------------

``fullname`` is simply a way of referencing credentials on a passpie. `Learn more <#fullname>`_

Is it possible to sync passpie using Dropbox?
-------------------------------------------

Yes, it is possible to sync a passpie database using cloud services like Dropbox or Google Drive.

Dropbox
+++++++

With default path ``~/.passpie`` and a Dropbox shared directory on path
``~/Dropbox``

::

    mv ~/.passpie ~/Dropbox/passpie    # move passpie db to Dropbox
    ln -s ~/Dropbox/passpie ~/.passpie # make a link to the db

Google Drive
++++++++++++

With default path ``~/.passpie`` and a Google Drive shared directory on
path ``~/GoogleDrive``

::

    mv ~/.passpie ~/GoogleDrive/passpie   # move passpie db to Google Drive
    ln -s ~/GoogleDrive/passpie ~.passpie # make a link to the db


Why is it taking so long to initialize a database?
--------------------------------------------------

Sometimes it takes a long time because of entropy on the host machine. It was noticed a long time on an ubuntu server(even more if it is a virtual machine). You could try using `haveged` to generate enough entropy.

On ubuntu:

::

   sudo apt-get install haveged

..

    You could also try this solution right here: http://serverfault.com/questions/214605/gpg-not-enough-entropy
