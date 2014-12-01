#########
Pysswords
#########

Pysswords encrypt your login credentials in a local file using the scrypt encryption.


************
Quickstart
************

.. code-block:: bash

    # Install pysswords
    pip install pysswords

    # create a new credentials database
    pysswords --create /path/to/password/file

    # add new credentials
    pysswords --add /path/to/password/file

    # get credential with name "example"
    pysswords --get "example" /path/to/password/file

    # search credentials with query "gmail"
    pysswords --search "gmail" /path/to/password/file

    # print all credentials as a table
    pysswords /path/to/password/file


*************
License (MIT)
*************

| Copyright © 2014 Marcwebbie, http://github.com/marcwebbie
|
| Permission is hereby granted, free of charge, to any person obtaining
| a copy of this software and associated documentation files (the
| "Software"), to deal in the Software without restriction, including
| without limitation the rights to use, copy, modify, merge, publish,
| distribute, sublicense, and/or sell copies of the Software, and to
| permit persons to whom the Software is furnished to do so, subject to
| the following conditions:
|
| The above copyright notice and this permission notice shall be
| included in all copies or substantial portions of the Software.
|
| THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
| EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
| MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
| NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
| LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
| OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
| WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
