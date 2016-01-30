from collections import namedtuple
import os
import shutil
import sys
import tempfile

import yaml

from passpie.importers import find_importer, BaseImporter, get_instances
from passpie.importers.default_importer import DefaultImporter
from passpie.importers.pysswords_importer import PysswordsImporter


def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


def test_find_importers_through_entry_points(mocker):
    from passpie import importers

    temp_dir = tempfile.mkdtemp()
    sys.path.insert(0, temp_dir)

    with open(os.path.join(temp_dir, 'fake_module.py'), 'w') as f:
        f.write("""\
from passpie.importers import BaseImporter

class FakeKeepassImporterClass(BaseImporter):
    pass
""")

    import pkg_resources
    fake_ep = pkg_resources.EntryPoint(
        'fake_keepass', 'fake_module',
        attrs=('FakeKeepassImporterClass', ))
    mock_iter_entry_points = mocker.patch(
        'pkg_resources.iter_entry_points',
        return_value=iter([fake_ep, ]))

    try:
        target_klass = None
        for klass in importers._get_importers_from_entry_points():
            if klass.__name__ == 'FakeKeepassImporterClass':
                target_klass = klass
                break

        mock_iter_entry_points.assert_called_once_with('passpie_importers')

        assert target_klass.__name__ == 'FakeKeepassImporterClass'
        assert target_klass.__module__ == 'fake_module'

    finally:
        sys.path.remove(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_all_yields_importers_from_entry_points(mocker):
    from passpie import importers

    class FakeImporter(importers.BaseImporter):
        pass
    fake_importers = {FakeImporter, }

    mocker.patch.object(importers, '__all__', new=[])
    mock_ep_finder = mocker.patch.object(
        importers, '_get_importers_from_entry_points',
        return_value=iter(fake_importers))

    found_importers = set(importers.get_all())
    assert found_importers == fake_importers
