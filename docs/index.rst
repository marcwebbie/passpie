Welcome to Passpie
==================

Passpie is a command line tool to  manage passwords from the terminal with a colorful and configurable interface. Use a master passphrase to decrypt login credentials, copy passwords to clipboard, syncronize with a git repository, check the state of your passwords, and more.

Password files are encrypted using `GnuPG <https://www.gnupg.org/>`_ and saved into yaml text files. Passpie supports **Linux**, **OSX** and **Windows**.

What does it look like?  Here is an example of a simple Passpie usage::

    passpie init
    passpie add foo@example.com --random
    passpie add bar@example.com --pattern "[0-9]{5}[a-z]{5}"
    passpie update foo@example --comment "Hello"
    passpie

Outputs::

    ╒═════════════╤═════════╤════════════╤═══════════╕
    │ Name        │ Login   │ Password   │ Comment   │
    ╞═════════════╪═════════╪════════════╪═══════════╡
    │ example.com │ bar     │ *****      │           │
    ├─────────────┼─────────┼────────────┼───────────┤
    │ example.com │ foo     │ *****      │ Hello     │
    ╘═════════════╧═════════╧════════════╧═══════════╛


Features
--------

| ★ Add, update, remove credentials
| ★ Manage multiple databases. Locally and remotely
| ★ Copy passwords to clipboard or to stdout
| ★ List credentials as a table with colored output
| ★ Search credentials by name, login, comments or regulax expresions
| ★ Group credentials by name
| ★ `Configuration <http://passpie.readthedocs.org/en/latest/configuration.html>`_ with ``~/.passpie`` or ``.config``
| ★ Version control passpie databases using git
| ★ Change passphrase and re-encrypt database
| ★ `Export credentials <getting_started.html#exporting-credentials>`_
| ★ `Import credentials <getting_started.html#importing-credentials>`_
| ★ Generate random passwords
| ★ Generate database status report
| ★ BASH/ZSH/FISH completion
| ★ Undo/Redo changes to the database. (requires `git <https://git-scm.com/>`_)
| ★ Set a personal gpg key recipient
| ★ Per database keyring

.. note:: This repository is open source and is available on `GitHub`_.
    We would love contributions.

.. _GitHub: https://github.com/marcwebbie/passpie


Documentation Contents
----------------------

This part of the documentation guides you through all of the passpie usage patterns.

.. toctree::
   :maxdepth: 2

   getting_started
   configuration
   contributing
   bugs_and_questions
   faq

Miscellaneous Pages
-------------------

.. toctree::
   :maxdepth: 2

   changelog
   license
