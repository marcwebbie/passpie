#########
Pysswords: Manage your passwords from the terminal
#########

.. image:: https://travis-ci.org/marcwebbie/pysswords.svg
    :target: https://travis-ci.org/marcwebbie/pysswords
.. image:: https://coveralls.io/repos/marcwebbie/pysswords/badge.png
  :target: https://coveralls.io/r/marcwebbie/pysswords


Pysswords lets you manage your login credentials from the terminal. All passwords are saved into an encrypted file. Only with the password you used to created you can view the file contents. If you want to know more about the encryption used, check the `Under the Hood`_ section.


**********
Installation
**********

.. code-block:: bash

    pip install pysswords


************
Quickstart
************

.. code-block:: bash

    # create a new credentials database
    pysswords --create /path/to/password/file

    # add new credentials
    pysswords --add /path/to/password/file

    # get credential with name "example"
    pysswords --get "example" /path/to/password/file

    # delete credential with name "example"
    pysswords --delete "example" /path/to/password/file

    # search credentials with query "gmail"
    pysswords --search "gmail" /path/to/password/file

    # print all credentials as a table
    pysswords /path/to/password/file


************
Contributing
************

+ fork the repository `<https://github.com/marcwebbie/pysswords/fork>`_
+ write your tests on :code:`tests/test.py`
+ if everything is OK. push your changes and make a pull request. ;)


**************
Under The Hood
**************

Encryption is done using the `PBKDF2 <http://en.wikipedia.org/wiki/PBKDF2>`_  derivation function and `SHA256 <http://en.wikipedia.org/wiki/SHA-2>`_ hashing by default.

Take a look at `pysswords.crypt <https://github.com/marcwebbie/pysswords/blob/master/pysswords/crypt.py>`_ module to know more.


*************
License (`MIT License <http://choosealicense.com/licenses/mit/>`_)
*************


The MIT License (MIT)

Copyright © 2014 Marc Webbie, http://github.com/marcwebbie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
