:code:`passpie`: Command-line password manager
*******************************************************

.. image:: https://raw.githubusercontent.com/marcwebbie/passpie/master/images/passpie2.png
    :align: center
    :width: 100%

|Version| |Build Status| |Windows Build Status| |Coverage|

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

..

    Check example remote passpie database: https://github.com/marcwebbie/passpiedb.

Install
========

.. code-block::

    pip install passpie

Or if you are on a mac, install via `Homebrew <http://brew.sh>`_:

.. code-block::

    brew install passpie


Learn more
================

Documentation: http://passpie.readthedocs.org
Mailing list: https://groups.google.com/d/forum/passpie
Gitter chat: https://gitter.im/marcwebbie/passpie
FAQ: http://passpie.readthedocs.org/en/latest/faq.html


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
.. |Gitter| image:: https://img.shields.io/gitter/room/marcwebbie/passpie.svg?style=flat-square
   :target: https://gitter.im/marcwebbie/passpie
.. |Version| image:: http://img.shields.io/pypi/v/passpie.svg?style=flat-square&label=latest%20version
   :target: https://pypi.python.org/pypi/passpie/
.. |License| image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
