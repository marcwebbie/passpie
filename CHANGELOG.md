# Changelog

## Versions

### 0.2

+ **√** Change completion script to passpie complete {zsh, bash}
+ **√** Fix unicode passwords handling
+ **√** Add `--to` option on `passpie copy`

### 0.1.5

+ **√** Bug fixes on installation issues

### 0.1.4

+ **√** Completion on credential fullnames

### 0.1.3

+ **√** Add remove in bulk using simple name syntax.
+ **√** Fix bug on missing xclip/xsel installation on ubuntu.

### 0.1.2

+ **√** Add `--copy` to clipboard option on `add` command: Thanks to [@vitalk](https://github.com/vitalk)
+ **√** Add bumpversion for cleaner `--version` option.

### 0.1.1

+ **√** Bug fix on unicode characters for passphrase
+ **√** Bug fix on regex for fullname split on python2

### 0.1

+ **√** Add `--force` option to overwrite when inserting credentials that exists

### v0.1rc7

+ **√** Support configurable random password generation
+ **√** Add query credential only by name
+ **√** Fix passpie utils handling bad config filepath
+ **√** Fix pysswords importer reading filepath

### v0.1rc6

+ **√** Bug fixes on loading user config
+ **√** Minor bug fixes
+ **√** Disable show_password config

### v0.1rc5

+ **√** Bug fixes on import command

### v0.1rc4

+ **√** Add Pysswords importer
+ **√** Fix bugs on default importer readfile

### v0.1rc3

+ **√** Bump invalid pypi version

### v0.1rc2.1

+ **√** Fix `reset` command not copying newly re-encrypted credentials

### v0.1rc2

+ **√** Add `reset` command. Reset passphrase and re-encrypt all credentials
+ **√** Bug fixes

### v0.1rc1

+ **√** Console interface
+ **√** Manage multiple databases
+ **√** Add, update, remove credentials
+ **√** Copy passwords to clipboard
+ **√** List credentials as a table
+ **√** Colored output
+ **√** Search credentials by name, login or comments
+ **√** Search with regular expression
+ **√** Grouping credentials
+ **√** Configuration by file
+ **√** Exporting Passpie database
+ **√** Importing Passpie database
+ **√** Randomly generated credential passwords
+ **√** Generate database status report
