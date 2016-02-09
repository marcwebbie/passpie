Version 1.4.0
-------------

+ **:heavy_check_mark:** Add support for empty passwords when adding credentials. closes #91
+ **:heavy_check_mark:** Add interactive edit with editor on cli.update. closes #87
+ **:heavy_check_mark:** Add interactive option to cli.add
+ **:heavy_check_mark:** Remove short_commands config. closes #93
+ **:heavy_check_mark:** Add command aliases support. closes #92
+ **:heavy_check_mark:** Add list credentials command: ``passpie list``
+ **:heavy_check_mark:** Refactor validators into validators module
+ **:heavy_check_mark:** Fix not loading global config on ``passpie config``
+ **:heavy_check_mark:** Add option config: ``passpie --config path/to/config``
+ **:heavy_check_mark:** Add hidden field configuration. closes #90
+ **:heavy_check_mark:** Fix import unicode on csv_importer
+ **:heavy_check_mark:** Fix not loading config from remote db. closes #89


Version 1.3.1
-------------

+ **:heavy_check_mark:** Fix cloning remote repository database

Version 1.3.0
-------------

+ **:heavy_check_mark:** Add config command: ``passpie config``
+ **:heavy_check_mark:** Fix process.Proc printing objects on Python3. fixes #88
+ **:heavy_check_mark:** Fix integration-test Makefile target
+ **:heavy_check_mark:** Fix keepass importer csv errors
+ **:heavy_check_mark:** Fix csv importing unicode chars
+ **:heavy_check_mark:** Add ``--clone`` option to cli.init
+ **:heavy_check_mark:** Add depth arg to clone function from cli.init
+ **:heavy_check_mark:** Fix python3 setup read README.rst
+ **:heavy_check_mark:** Fix config path to remote repo. fixes #86

Version 1.2.0
-------------

+ **:heavy_check_mark:** Add configurable master csv importer
+ **:heavy_check_mark:** Fix cli ``--importer`` name on import command
+ **:heavy_check_mark:** Add Keepass csv importer. fixes #32
+ **:heavy_check_mark:** Add ``--importers`` option to import
+ **:heavy_check_mark:** Fix genpass raising re.error on pattern error fixes #84
+ **:heavy_check_mark:** Set ``--pattern`` option as standalone
+ **:heavy_check_mark:** Fix passpie complete commands for shells
+ **:heavy_check_mark:** Fix tests on creating repository for git init
+ **:heavy_check_mark:** Fix error creating subdir in database in git init

Version 1.1.1
-------------

+ **:heavy_check_mark:** Fix filtering by fullname without login
+ **:heavy_check_mark:** Update colors on copy message

Version 1.1.0
-------------

+ **:heavy_check_mark:** Add volatile passpie repo using git url as path: ``passpie -D https://foo@example.com/user/repo.git``.
+ **:heavy_check_mark:** Add autopush git remote history.
+ **:heavy_check_mark:** Set default config recipient to ``null``.
+ **:heavy_check_mark:** Fix error on passpie init raising exception when path exists. Closes #83

Version 1.0.2
-------------

+ **:heavy_check_mark:** Fix passpie update command values in wrong order

Version 1.0.1
-------------

+ **:heavy_check_mark:** Fix missing ``--passphrase`` option to init

Version 1.0.0
-------------

+ **:heavy_check_mark:** Fix runtime permission issues
+ **:heavy_check_mark:** Add local database config files with ``.config``
+ **:heavy_check_mark:** Add auto-pull git remote history. fixes #72
+ **:heavy_check_mark:** Support default system keychain via config ``recipient``. fixes #45
+ **:heavy_check_mark:** Support filename extension ``.pass`` configurable. fixes #47
+ **:heavy_check_mark:** Support regex pattern generated passwords. fixes #62
+ **:heavy_check_mark:** Fix --random/--password error when passing from command. fixes #82
+ **:heavy_check_mark:** Improve ensure passphrase function
+ **:heavy_check_mark:** Fix fullname filtering credentials


Version 0.3.3
-------------

+ **:heavy_check_mark:** Fix issue on ``reset-to`` not reseting from ``passpie log``
+ **:heavy_check_mark:** Fix issue on copy to clipboard on ``cygwin`` platform

Version 0.3.2
-------------

+ **:heavy_check_mark:** Minor fix on cryptor find binary

Version 0.3.1
-------------

+ **:heavy_check_mark:** Minor fix on which command not following symlinks on gnupg

Version 0.3
-------------

+ **:heavy_check_mark:** Support version control passpie database with git
+ **:heavy_check_mark:** Minor bug fixes

Version 0.2.2
-------------

+ **:heavy_check_mark:** Support ``gpg2`` binary
+ **:heavy_check_mark:** Fix linux missing commands for copy to clipboard. thanks to @jpiron

Version 0.2.1
-------------

+ **:heavy_check_mark:** Fix update credential password from prompt

Version 0.2
-------------

+ **:heavy_check_mark:** Change completion script to passpie complete {zsh, bash}
+ **:heavy_check_mark:** Fix unicode passwords handling
+ **:heavy_check_mark:** Add ``--to`` option on ``passpie copy``

Version 0.1.5
-------------

+ **:heavy_check_mark:** Bug fixes on installation issues

Version 0.1.4
-------------

+ **:heavy_check_mark:** Completion on credential fullnames

Version 0.1.3
-------------

+ **:heavy_check_mark:** Add remove in bulk using simple name syntax.
+ **:heavy_check_mark:** Fix bug on missing xclip/xsel installation on ubuntu.

Version 0.1.2
-------------

+ **:heavy_check_mark:** Add ``--copy`` to clipboard option on ``add`` command: Thanks to `@vitalk <https://github.com/vitalk>`_
+ **:heavy_check_mark:** Add bumpversion for cleaner ``--version`` option.

Version 0.1.1
-------------

+ **:heavy_check_mark:** Bug fix on unicode characters for passphrase
+ **:heavy_check_mark:** Bug fix on regex for fullname split on python2

Version 0.1
-------------

+ **:heavy_check_mark:** Add ``--force`` option to overwrite when inserting credentials that exists

Version 0.1rc7
---------------

+ **:heavy_check_mark:** Support configurable random password generation
+ **:heavy_check_mark:** Add query credential only by name
+ **:heavy_check_mark:** Fix passpie utils handling bad config filepath
+ **:heavy_check_mark:** Fix pysswords importer reading filepath

Version 0.1rc6
--------------

+ **:heavy_check_mark:** Bug fixes on loading user config
+ **:heavy_check_mark:** Minor bug fixes
+ **:heavy_check_mark:** Disable show_password config

Version 0.1rc5
--------------

+ **:heavy_check_mark:** Bug fixes on import command

Version 0.1rc4
--------------

+ **:heavy_check_mark:** Add Pysswords importer
+ **:heavy_check_mark:** Fix bugs on default importer readfile

Version 0.1rc3
--------------

+ **:heavy_check_mark:** Bump invalid pypi version

Version 0.1rc2.1
----------------

+ **:heavy_check_mark:** Fix ``reset`` command not copying newly re-encrypted credentials

Version 0.1rc2
--------------

+ **:heavy_check_mark:** Add ``reset`` command. Reset passphrase and re-encrypt all credentials
+ **:heavy_check_mark:** Bug fixes

Version 0.1rc1
--------------

+ **:heavy_check_mark:** Console interface
+ **:heavy_check_mark:** Manage multiple databases
+ **:heavy_check_mark:** Add, update, remove credentials
+ **:heavy_check_mark:** Copy passwords to clipboard
+ **:heavy_check_mark:** List credentials as a table
+ **:heavy_check_mark:** Colored output
+ **:heavy_check_mark:** Search credentials by name, login or comments
+ **:heavy_check_mark:** Search with regular expression
+ **:heavy_check_mark:** Grouping credentials
+ **:heavy_check_mark:** Configuration by file
+ **:heavy_check_mark:** Exporting Passpie database
+ **:heavy_check_mark:** Importing Passpie database
+ **:heavy_check_mark:** Randomly generated credential passwords
+ **:heavy_check_mark:** Generate database status report
