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
