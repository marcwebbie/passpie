# Configuring Passpie

#### `path`

Path to default database

```yaml
# default
path: ~/.passpie
```

#### `homedir`

Path to gnupg homedir

> Ignored if `.keys` exists in database

#### `recipient`

Default gpg recipient to encrypt/decrypt credentials using keychains. This should be either recipient fingerprint or email.

```yaml
# default
recipient: passpie@local
```

> Ignored if `.keys` exists in database

#### `key_length`

Key generation length. The lengths range from 1024 to 4096 bits

#### `repo`

Create a git repo by default when database is initialized

```yaml
# default
repo: true
```

#### `autopull`

Automatically pull changes from git remote repository. This setting should be a list of remote/branch

```yaml
# default
autopull: null
```

This setting should be a list containing `remote` and  `branch` to pull.

```yaml
autopull:
- origin  # remote
- master  # branch
```

#### `autopush`

Automatically push to a git remote repository. This setting should be a list of remote/branch

```yaml
# default
autopush: null
```

This setting should be a list containing `remote` and  `branch` to pull.

```yaml
autopull:
- origin  # remote
- master  # branch
```

> Useful when used with a volatile database. `passpie -D https://foo@example.com/user/repo.git --autopush "origin/master"`

#### `copy_timeout`

Automatically clear clipboard when timeout is expired. Timeout is in seconds

```
#default
copy_timeout: 0
```

#### `short_commands`

Use passpie commands with short aliases. Like `passpie a` for `passpie add`

```yaml
# default
short_commands: false
```

##### Choices:

- true
- false

#### `status_repeated_passwords_limit`

```yaml
# default
status_repeated_passwords_limit: 0
```

Repeat credential fullname on status list

#### `extension`

Credential files configurable extension

```yaml
# default
extension: .pass
```

#### `genpass_pattern`

Regular expression pattern to password generation

```yaml
# default
genpass_pattern: "[a-z]{5} [-_+=*&%$#]{5} [A-Z]{5}"
```

Regular expression pattern used to generate random passwords

#### `headers`

Credential columns to be printed

```yaml
# default
headers:
  - name
  - login
  - password
  - comment
```

##### Choices:

- name
- login
- password
- comment

#### `table_format`

Defines how the Table is formated

```yaml
# default
table_format: fancy_grid
```

##### Choices:

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

#### `colors`

Column data colors

##### Default: `{"login": "green", "name": "yellow"}`

##### Choices:

- black
- red
- green
- yellow
- blue
- magenta
- cyan
- white
