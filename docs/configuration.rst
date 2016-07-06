Configuration
=============

Passie configuration files are ``yaml`` files. Passpie supports local and global configuration files. To set a local database.

global passpie configuration files lives in ``~/.passpierc`` while local configuration files lives in database directory as a ``.config`` file.

Examples
--------

Full config file
++++++++++++++++

.. code-block:: yaml

    COPY_TIMEOUT: 0
    DATABASE: passpie.db
    GIT: true
    HOMEDIR: /Users/marc/.gnupg
    KEY_LENGTH: 4096
    PASSWORD_PATTERN: '[a-zA-Z0-9=+_*!?&%$# ]{32}'
    PUSH: null
    RANDOM_PASSWORD: false
    RECIPIENT: null
    TABLE_FIELDS:
    - name
    - login
    - password
    - comment
    TABLE_FORMAT: fancy_grid
    TABLE_HIDDEN_STRING: '********'
    TABLE_STYLE:
      login:
        fg: green
      name:
        fg: yellow

Partial configuration file
++++++++++++++++++++++++++

.. code-block:: yaml

   RECIPIENT: john.doe@example.com
   COPY_TIMEOUT: 10
   TABLE_FORMAT: rst


``DATABASE``
-----------------------------------

| **Default:** ``passpie.db``
| **Description:** Path to default database.
|

``HOMEDIR``
-----------------------------------

| **Default:** ``null``
| **Description:** Path to default gnupg homedir.
|

``PUSH``
-----------------------------------

| **Default:** ``null``
| **Description:** Automatically push changes from remote git repository.
|

``RECIPIENT``
-----------------------------------

| **Default:** ``null``
| **Description:** GnuPG defaul recipient. This can be a fingerprint/emai/name.
|

.. warning::

   If ``RECIPIENT`` is not ``null`` user must also set ``HOMEDIR``


``COPY_TIMEOUT``
-----------------------------------

| **Default:** ``0``
| **Description:** Automatically clear clipboard N seconds after copy
|

``PASSWORD_PATTERN``
-----------------------------------

| **Default:** ``"[a-z]{5} [-_+=*&%$#]{5} [A-Z]{5}"``
| **Description:** Regex pattern for password random generation
|

``TABLE_FIELDS``
-----------------------------------

| **Default:** ``["name", "login", "password", "comment"]``
| **Description:** Tables fields to print
|

``TABLE_FORMAT``
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

``HEADERS``
-----------------------------------

| **Default:** ``[name, login, password, comments]``
| **Description:** Column names to show on table
|

``PASSWORD_HIDDEN_STRING``
-----------------------------------

| **Default:** ``********``
| **Description:** Text to be used with ``hidden`` as replacement for hidden columns
|

``KEY_LENGTH``
-----------------------------------

| **Default:** ``4096``
| **Description:** AES encryption key length

.. warning::

   Use a strong primary key. Some people still have 1024-bit AES keys.
   You really should transition to a stronger bit-length and hashing algo.
   It is recommend to make a 2048 or 4096-bit key.

   Also have a look at `GnuPG documentation <https://www.gnupg.org/gph/en/manual.html#AEN494>`_ on keys

``GIT``
-----------------------------------

| **Default:** ``true``
| **Description:** Automatically create a git repository in database on initialization
|
