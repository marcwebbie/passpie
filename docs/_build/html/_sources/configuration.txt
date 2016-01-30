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

Values:

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
| **Description:** Column names
|

``colors``
-----------------------------------

| **Default:** ``{login: green, name: yellow}``
| **Description:** Table column colors

Values:

- green
- yellow
- blue
- red
- white
- gray
- magenta
- cyan

``key_length``
-----------------------------------

| **Default:** ``4096``
| **Description:** AES encryption key length

.. warning::

   Use a strong primary key.
   Some people still have 1024-bit DSA keys. You really should transition to a stronger bit-length and hashing algo. In 2011, the US government instution NIST has deprecated DSA-1024, since 2013 it is even disallowed.

   It is recommend to make a 4096bit RSA key, with the sha512 hashing algo, making a transition statement that is signed by both keys, and then letting people know. Also have a look at this good document that details exactly the steps that you need to create such a key, making sure that you are getting the right hashing algo (it can be slightly complicated if you are using GnuPG versions less than 1.4.10).

``repo``
-----------------------------------

| **Default:** ``true``
| **Description:** Automatically create a git repository in database on initialization
|

``short_commands``
-----------------------------------

| **Default:** ``false``
| **Description:** Use alias for passpie commands
|

``status_repeated_passwords_limit``
-----------------------------------

| **Default:** ``5``
| **Description:** Number of credentials to show on the repeated column of status
