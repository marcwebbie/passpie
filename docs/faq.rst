FAQ
===

What is a passpie database?
---------------------------

Passpie database is structured in a directory hierachy. Every credential
is a ``.pass`` file inside a directory named after a credential group.

An empty database would look like this:

.. code:: bash

    passpie --database /tmp/passpie init

    tree /tmp/passpie -la
    # /tmp/passpie
    # └── .keys

After adding a new credential the database would look like this:

.. code:: bash

    passpie --database /tmp/passpie add octocat@github.com
    # Password: **********

    tree /tmp/passpie -la
    # /tmp/passpie
    # ├── .keys
    # └── github.com
    #     └── octocat.pass

If we add more credentials to group github.com. Directory structure
would be:

.. code:: bash

    passpie --database /tmp/passpie add octocat2@github.com
    # Password: **********

    tree /tmp/passpie -la
    # /tmp/passpie
    # ├── .keys
    # └── github
    #     └── octocat.pass
    #     └── octocat2.pass

What is a fullname?
-------------------

``fullname`` is simply a way of referencing credentials on a passpie. `Learn more <#fullname>`_

Is it possible to sync passpie using Dropbox?
---------------------------------------------

Yes, it is possible to sync a passpie database using cloud services like Dropbox or Google Drive.

Dropbox
+++++++

With default path ``~/.passpie`` and a Dropbox shared directory on path
``~/Dropbox``

::

    mv ~/.passpie ~/Dropbox/passpie    # move passpie db to Dropbox
    ln -s ~/Dropbox/passpie ~/.passpie # make a link to the db

Google Drive
++++++++++++

With default path ``~/.passpie`` and a Google Drive shared directory on
path ``~/GoogleDrive``

::

    mv ~/.passpie ~/GoogleDrive/passpie   # move passpie db to Google Drive
    ln -s ~/GoogleDrive/passpie ~.passpie # make a link to the db


Why is it taking so long to initialize a database?
--------------------------------------------------

Sometimes it takes a long time because of entropy on the host machine. It was noticed a long time on an ubuntu server(even more if it is a virtual machine). You could try using `haveged` to generate enough entropy.

On ubuntu:

::

   sudo apt-get install haveged

..

    You could also try this solution right here: http://serverfault.com/questions/214605/gpg-not-enough-entropy
