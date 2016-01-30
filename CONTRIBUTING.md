# Contributing

Whether reporting bugs, discussing improvements and new ideas or writing
extensions: Contributions to Passpie are welcome! Here's how to get started:

1. Check for open issues or open a fresh issue to start a discussion around
   a feature idea or a bug
2. Fork the repository <https://github.com/marcwebbie/passpie/>
   clone your fork and start making your changes
3. Write a test which shows that the bug was fixed or that the feature works
   as expected
4. Send a pull request and bug the maintainer until it gets merged and
   published ☺

## Importers

Importers should be independent pluggable code. To add a new importer. Create python module into importers package. If you were writting an importer to a site called `superpassword`.

```fish
touch passpie/importers/superpassword.py
```

This importer should inherit from `passpie.importers.BaseImporter` and override two methods:

+ `match`: This method should check file passed as filepath and see if it is parseable and can be read by importer

+ `handle`: Return parsed credentials from file. The return must be a list of credentials with plain text passwords


```python
from passpie.importers import BaseImporter


class DefaultImporter(BaseImporter):

    def match(self, filepath):
        return True

    def handle(self, filepath):
        credentials = []
        return credentials
```
