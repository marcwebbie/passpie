Configuration
=============

Passie configuration files are ``yaml`` files. Passpie supports local and global configuration files. To set a local database.

global passpie configuration files lives in ``~/.passpierc`` while local configuration files lives in database directory as a ``.config`` file.

Examples
--------

Full passpie configuration file
+++++++++++++++++++++++++++++++

.. code-block:: yaml

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
   recipient: null
   repo: true
   status_repeated_passwords_limit: 5
   table_format: fancy_grid

Partial configuration file
++++++++++++++++++++++++++

.. code-block:: yaml

   recipient: marcwebbie@example.com
   copy_timeout: 10
   extension: .gpg
   table_format: rst

Debugging
---------

For debugging, it might be useful to check actual passpie configuration for your commands::

  # Global configuration found on ~/.passpierc
  passpie config global

  # Local configuration found on $PASSPIE_DATABASE/.config
  passpie config local

Current config
++++++++++++++

Current configuration with all overriden variables::

  passpie config current

OR::

  passpie config

..

.. note::

   If you have pygments installed, to have colored output on the config::

     passpie config | pygmentize -l YAML

Options
-------

``path``
-----------------------------------

| **Default:** ``~/.passpie``
| **Description:** Path to default database.
|

``homedir``
-----------------------------------

| **Default:** ``~/.gnupg``
| **Description:** Path to default gnupg homedir.
|

``autopull``
-----------------------------------

| **Default:** ``null``
| **Description:** Automatically pull changes from remote git repository.
|

``autopush``
-----------------------------------

| **Default:** ``null``
| **Description:** Automatically pull changes from remote git repository.
|

``recipient``
-----------------------------------

| **Default:** ``null``
| **Description:** GnuPG defaul recipient. This can be a fingerprint/emai/name.
|

``extension``
-----------------------------------

| **Default:** ``.pass``
| **Description:** Password files extension
|

``copy_timeout``
-----------------------------------

| **Default:** ``0``
| **Description:** Automatically clear clipboard after n seconds
|

``genpass_pattern``
-----------------------------------

| **Default:** ``"[a-z]{5} [-_+=*&%$#]{5} [A-Z]{5}"``
| **Description:** Regex pattern for password random generation
|

``table_format``
-----------------------------------

| **Default:** ``fancy_grid``
| **Description:** Render table format
|

Supported table formats:

- plain
- simple
- grid
- fancy_grid
- pipe
- orgtbl
- jira
- psql
- rst
- mediawiki
- moinmoin
- html
- latex
- latex_booktabs
- textile

``headers``
-----------------------------------

| **Default:** ``[name, login, password, comments]``
| **Description:** Column names to show on table
|


``hidden``
-----------------------------------

| **Default:** ``[password]``
| **Description:** Column names to hide values when printing. Uses ``hidden_string`` as replaced text
|


``hidden_string``
-----------------------------------

| **Default:** ``********``
| **Description:** Text to be used with ``hidden`` as replacement for hidden columns
|

``colors``
-----------------------------------

| **Default:** ``{login: green, name: yellow}``
| **Description:** Table column colors

Supported color names:

- black (might be a gray)
- red
- green
- yellow (might be an orange)
- blue
- magenta
- cyan
- white (might be light gray)
- reset (reset the color code only)

``key_length``
-----------------------------------

| **Default:** ``4096``
| **Description:** AES encryption key length

.. warning::

   Use a strong primary key. Some people still have 1024-bit AES keys.
   You really should transition to a stronger bit-length and hashing algo.
   It is recommend to make a 2048 or 4096-bit key.

   Also have a look at `GnuPG documentation <https://www.gnupg.org/gph/en/manual.html#AEN494>`_ on keys

``repo``
-----------------------------------

| **Default:** ``true``
| **Description:** Automatically create a git repository in database on initialization
|

``status_repeated_passwords_limit``
-----------------------------------

| **Default:** ``5``
| **Description:** Number of credentials to show on the repeated column of status
