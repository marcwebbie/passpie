:code:`passpie`: Comand-line password manager
*******************************************************

.. image:: https://badges.gitter.im/marcwebbie/passpie.svg
   :alt: Join the chat at https://gitter.im/marcwebbie/passpie
   :target: https://gitter.im/marcwebbie/passpie?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://raw.githubusercontent.com/marcwebbie/passpie/master/images/passpie.png
    :align: center
    :width: 100%

|Version| |Build Status| |Windows Build Status| |Coverage| |Requirements|

Passpie is a command line tool to  manage passwords from the terminal with a colorful and configurable interface. Password files are encrypted using `GnuPG <http://en.wikipedia.org/wiki/GNU_Privacy_Guard)>`_ and saved into yaml text files. Use a master passphrase to decrypt login credentials, copy passwords to clipboard, syncronize with a git repository, check the state of your passwords, and more...


Install
========

.. code-block::

    pip install passpie

Or if you are on a mac, install via `Homebrew <http://brew.sh>`_:

.. code-block::

    brew install passpie


Quickstart
==========

.. code-block::

    passpie init
    passpie add foo@example.com --random --pattern "[0-9]{5}[a-z]{5}"
    passpie add bar@example.com --random --pattern "[0-9]{5}[a-z]{5}"
    passpie update foo@example.com --comment "Hello"
    passpie

Outputs:

.. code-block::

    ╒═════════════╤═════════╤════════════╤═══════════╕
    │ Name        │ Login   │ Password   │ Comment   │
    ╞═════════════╪═════════╪════════════╪═══════════╡
    │ example.com │ bar     │ *****      │           │
    ├─────────────┼─────────┼────────────┼───────────┤
    │ example.com │ foo     │ *****      │ Hello     │
    ╘═════════════╧═════════╧════════════╧═══════════╛


Documentation
================

Read full documentation on http://passpie.readthedocs.org

And visit our chat on |Gitter|


Licence |License|
=================

Copyright (c) 2014-2016 Marcwebbie, <http://github.com/marcwebbie>

Full license here: `LICENSE <https://github.com/marcwebbie/passpie/blob/master/LICENSE>`_


.. |Build Status| image:: http://img.shields.io/travis/marcwebbie/passpie.svg?style=flat-square
   :target: https://travis-ci.org/marcwebbie/passpie
.. |Windows Build Status| image:: https://img.shields.io/appveyor/ci/marcwebbie/passpie.svg?style=flat-square&label=windows%20build
   :target: https://ci.appveyor.com/project/marcwebbie/passpie
.. |Coverage| image:: http://img.shields.io/coveralls/marcwebbie/passpie.svg?style=flat-square
   :target: https://coveralls.io/r/marcwebbie/passpie
.. |Requirements| image:: http://img.shields.io/requires/github/marcwebbie/passpie.svg?style=flat-square
   :target: https://requires.io/github/marcwebbie/passpie/requirements/?branch=master
.. |Gitter| image:: https://img.shields.io/gitter/room/marcwebbie/passpie.svg?style=flat-square
   :target: https://gitter.im/marcwebbie/passpie
.. |Version| image:: http://img.shields.io/pypi/v/passpie.svg?style=flat-square&label=latest%20version
   :target: https://pypi.python.org/pypi/passpie/
.. |License| image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
