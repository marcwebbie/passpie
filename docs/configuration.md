# Global configuration

## `path =`

**default** ~/.passpie

Path to passpie database

## `short_commands = (true | false)`

**default** false

Use passpie commands with short aliases. Like `passpie a` for `passpie add`

## `genpass_length =`

**default:** `32`

Length of randomly generated passwords with option `--random`

## `genpass_symbols =`

**default:** `"_-#|+= "`

Symbols used on random password generation

## `homedir =`

**default** ~/.gnupg

**required:** False

Path to gnupg homedir

> This path will not be used if .keys are found on database path

## `recipient =`

**default** passpie@local

**required:** False

Default gpg recipient to encrypt/decrypt credentials

## `table_format = (fancy_grid | rst | simple | orgtbl | pipe | grid | plain | latex)`

**default:** `fancy_grid`

Table format when listing credentials

## `headers = (name | login | password | comment | fullname)`

**default:**

```
headers:
  - name
  - login
  - password
  - comment
```

## `colors = (green | red | blue | white | cyan | magenta | yellow)`

**default:**

```
colors:
  name: yellow
  login: green
```

## `git = (true | false)`

**default:** true

Create a git repository on the database directory when git is available.

[learn more](#version-control-your-database)

## `search_automatic_regex = (true | false)`

**default:** false

Automatically transform the search pattern into a regex if the search pattern is a word (ie: add .* prefix and suffix)

## `status_repeated_passwords_limit=`

**default:** 5

Set an upper limit to display the number of credentials with the same password instead of displaying the credentials themselves. This is avoid the uggly table rendering when the passords list doesn't fit on one line. Currently [Tabulate](https://pypi.python.org/pypi/tabulate) doesn't handle line wraps.
