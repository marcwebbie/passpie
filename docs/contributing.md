# Contributing to Passpie

## Coding

### Quickstart

```fish
git clone https://github.com/marcwebbie/passpie.git
cd passpie
virtualenv .venv && source .venv/bin/activate
make develop
make
```

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
