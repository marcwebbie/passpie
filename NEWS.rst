Version 1.4.3
-------------
+ **✔** Fix update credential password encrypts empty string
+ **✔** Default to an empty dict instead of None

Version 1.4.2
-------------

+ **✔** Fix passpie update using only fullname query by name

Version 1.4.1
-------------

+ **✔** Fix string literals unicode tests

Version 1.4.0
-------------

+ **✔** Add support for empty passwords when adding credentials. closes #91
+ **✔** Add interactive edit with editor on cli.update. closes #87
+ **✔** Add interactive option to cli.add
+ **✔** Remove short_commands config. closes #93
+ **✔** Add command aliases support. closes #92
+ **✔** Add list credentials command: ``passpie list``
+ **✔** Refactor validators into validators module
+ **✔** Fix not loading global config on ``passpie config``
+ **✔** Add option config: ``passpie --config path/to/config``
+ **✔** Add hidden field configuration. closes #90
+ **✔** Fix import unicode on csv_importer
+ **✔** Fix not loading config from remote db. closes #89


Version 1.3.1
-------------

+ **✔** Fix cloning remote repository database

Version 1.3.0
-------------

+ **✔** Add config command: ``passpie config``
+ **✔** Fix process.Proc printing objects on Python3. fixes #88
+ **✔** Fix integration-test Makefile target
+ **✔** Fix keepass importer csv errors
+ **✔** Fix csv importing unicode chars
+ **✔** Add ``--clone`` option to cli.init
+ **✔** Add depth arg to clone function from cli.init
+ **✔** Fix python3 setup read README.rst
+ **✔** Fix config path to remote repo. fixes #86

Version 1.2.0
-------------

+ **✔** Add configurable master csv importer
+ **✔** Fix cli ``--importer`` name on import command
+ **✔** Add Keepass csv importer. fixes #32
+ **✔** Add ``--importers`` option to import
+ **✔** Fix genpass raising re.error on pattern error fixes #84
+ **✔** Set ``--pattern`` option as standalone
+ **✔** Fix passpie complete commands for shells
+ **✔** Fix tests on creating repository for git init
+ **✔** Fix error creating subdir in database in git init

Version 1.1.1
-------------

+ **✔** Fix filtering by fullname without login
+ **✔** Update colors on copy message

Version 1.1.0
-------------

+ **✔** Add volatile passpie repo using git url as path: ``passpie -D https://foo@example.com/user/repo.git``.
+ **✔** Add autopush git remote history.
+ **✔** Set default config recipient to ``null``.
+ **✔** Fix error on passpie init raising exception when path exists. Closes #83

Version 1.0.2
-------------

+ **✔** Fix passpie update command values in wrong order

Version 1.0.1
-------------

+ **✔** Fix missing ``--passphrase`` option to init

Version 1.0.0
-------------

+ **✔** Fix runtime permission issues
+ **✔** Add local database config files with ``.config``
+ **✔** Add auto-pull git remote history. fixes #72
+ **✔** Support default system keychain via config ``recipient``. fixes #45
+ **✔** Support filename extension ``.pass`` configurable. fixes #47
+ **✔** Support regex pattern generated passwords. fixes #62
+ **✔** Fix --random/--password error when passing from command. fixes #82
+ **✔** Improve ensure passphrase function
+ **✔** Fix fullname filtering credentials


Version 0.3.3
-------------

+ **✔** Fix issue on ``reset-to`` not reseting from ``passpie log``
+ **✔** Fix issue on copy to clipboard on ``cygwin`` platform

Version 0.3.2
-------------

+ **✔** Minor fix on cryptor find binary

Version 0.3.1
-------------

+ **✔** Minor fix on which command not following symlinks on gnupg

Version 0.3
-------------

+ **✔** Support version control passpie database with git
+ **✔** Minor bug fixes

Version 0.2.2
-------------

+ **✔** Support ``gpg2`` binary
+ **✔** Fix linux missing commands for copy to clipboard. thanks to @jpiron

Version 0.2.1
-------------

+ **✔** Fix update credential password from prompt

Version 0.2
-------------

+ **✔** Change completion script to passpie complete {zsh, bash}
+ **✔** Fix unicode passwords handling
+ **✔** Add ``--to`` option on ``passpie copy``

Version 0.1.5
-------------

+ **✔** Bug fixes on installation issues

Version 0.1.4
-------------

+ **✔** Completion on credential fullnames

Version 0.1.3
-------------

+ **✔** Add remove in bulk using simple name syntax.
+ **✔** Fix bug on missing xclip/xsel installation on ubuntu.

Version 0.1.2
-------------

+ **✔** Add ``--copy`` to clipboard option on ``add`` command: Thanks to `@vitalk <https://github.com/vitalk>`_
+ **✔** Add bumpversion for cleaner ``--version`` option.

Version 0.1.1
-------------

+ **✔** Bug fix on unicode characters for passphrase
+ **✔** Bug fix on regex for fullname split on python2

Version 0.1
-------------

+ **✔** Add ``--force`` option to overwrite when inserting credentials that exists

Version 0.1rc7
---------------

+ **✔** Support configurable random password generation
+ **✔** Add query credential only by name
+ **✔** Fix passpie utils handling bad config filepath
+ **✔** Fix pysswords importer reading filepath

Version 0.1rc6
--------------

+ **✔** Bug fixes on loading user config
+ **✔** Minor bug fixes
+ **✔** Disable show_password config

Version 0.1rc5
--------------

+ **✔** Bug fixes on import command

Version 0.1rc4
--------------

+ **✔** Add Pysswords importer
+ **✔** Fix bugs on default importer readfile

Version 0.1rc3
--------------

+ **✔** Bump invalid pypi version

Version 0.1rc2.1
----------------

+ **✔** Fix ``reset`` command not copying newly re-encrypted credentials

Version 0.1rc2
--------------

+ **✔** Add ``reset`` command. Reset passphrase and re-encrypt all credentials
+ **✔** Bug fixes

Version 0.1rc1
--------------

+ **✔** Console interface
+ **✔** Manage multiple databases
+ **✔** Add, update, remove credentials
+ **✔** Copy passwords to clipboard
+ **✔** List credentials as a table
+ **✔** Colored output
+ **✔** Search credentials by name, login or comments
+ **✔** Search with regular expression
+ **✔** Grouping credentials
+ **✔** Configuration by file
+ **✔** Exporting Passpie database
+ **✔** Importing Passpie database
+ **✔** Randomly generated credential passwords
+ **✔** Generate database status report
