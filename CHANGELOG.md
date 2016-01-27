# Changelog

## Versions

### 1.1.1

+ **√** Fix filtering by fullname without login
+ **√** Update colors on copy message

### 1.1.0

+ **√** Add volatile passpie repo using git url as path: `passpie -D https://foo@example.com/user/repo.git`.
+ **√** Add autopush git remote history.
+ **√** Set default config recipient to `null`.
+ **√** Fix error on passpie init raising exception when path exists. Closes #83

### 1.0.2

+ **√** Fix passpie update command values in wrong order

### 1.0.1

+ **√** Fix missing `--passphrase` option to init

### 1.0.0

+ **√** Fix runtime permission issues
+ **√** Add local database config files with `.config`
+ **√** Add auto-pull git remote history. fixes #72
+ **√** Support default system keychain via config `recipient`. fixes #45
+ **√** Support filename extension `.pass` configurable. fixes #47
+ **√** Support regex pattern generated passwords. fixes #62
+ **√** Fix --random/--password error when passing from command. fixes #82
+ **√** Improve ensure passphrase function
+ **√** Fix fullname filtering credentials


### 0.3.3

+ **√** Fix issue on `reset-to` not reseting from `passpie log`
+ **√** Fix issue on copy to clipboard on `cygwin` platform

### 0.3.2

+ **√** Minor fix on cryptor find binary

### 0.3.1

+ **√** Minor fix on which command not following symlinks on gnupg

### 0.3

+ **√** Support version control passpie database with git
+ **√** Minor bug fixes

### 0.2.2

+ **√** Support `gpg2` binary
+ **√** Fix linux missing commands for copy to clipboard. thanks to @jpiron

### 0.2.1

+ **√** Fix update credential password from prompt

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
