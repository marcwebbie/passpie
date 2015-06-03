import datetime
import re

try:
    from mock import Mock, mock_open
except ImportError:
    from unittest.mock import Mock, mock_open

import py
import py.path
import pytest

from passpie.importers import kppy_importer


def test_kppy_matching_returns_false_when_kppy_is_not_installed(mocker):
    mocker.patch.object(kppy_importer, '_found_kppy', False)
    importer = kppy_importer.KppyImporter()
    importer.log = Mock()

    res = importer.match('dummy')

    assert res is False
    assert importer.log.called
    importer.log.assert_called_once_with('kppy is not installed')


def test_kppy_matching_returns_false_when_path_to_match_is_not_a_file(mocker):
    mocker.patch.object(kppy_importer, '_found_kppy', True)
    importer = kppy_importer.KppyImporter()
    importer.log = Mock()
    mock_isfile = mocker.patch('os.path.isfile', return_value=False)
    filepath = 'dummy'

    res = importer.match(filepath)

    assert res is False
    assert importer.log.called
    importer.log.assert_called_once_with(
        'Filepath "{}" is not a file'.format(filepath))


def test_kppy_matching_returns_false_when_filepath_extension_is_not_kdb(mocker):
    mocker.patch.object(kppy_importer, '_found_kppy', True)
    importer = kppy_importer.KppyImporter()
    importer.log = Mock()
    mock_isfile = mocker.patch('os.path.isfile', return_value=True)
    filepath = 'dummy.hello'

    res = importer.match(filepath)

    assert res is False
    assert importer.log.called
    importer.log.assert_called_once_with(
        'Filepath "{}" is not a Keepass database'.format(filepath))


def test_kppy_matching_returns_true(mocker):
    mocker.patch.object(kppy_importer, '_found_kppy', True)
    importer = kppy_importer.KppyImporter()
    importer.log = Mock()
    mock_isfile = mocker.patch('os.path.isfile', return_value=True)
    filepath = 'dummy.kdb'

    res = importer.match(filepath)

    assert res is True
    assert not importer.log.called


@pytest.fixture
def empty_kppy_db(request, tmpdir):
    assert isinstance(tmpdir, py.path.local)
    kdb_path = tmpdir.join('test_db.kdb')

    from kppy.database import KPDBv1, KPError
    db = KPDBv1(str(kdb_path), password='test_pass', new=True)

    def cleanup():
        db.close()

    return db


class TestWithAKeepassDb(object):

    @pytest.fixture(autouse=True)
    def kppy_db(self, request, empty_kppy_db):
        from kppy.database import KPDBv1, KPError
        from kppy.groups import v1Group
        assert isinstance(empty_kppy_db, KPDBv1)

        assert len(empty_kppy_db.groups) == 1
        root_group = empty_kppy_db.groups[0]

        creation_time = datetime.datetime.utcnow()
        creation_time = datetime.datetime(*creation_time.utctimetuple()[:6])
        empty_kppy_db.mock_creation_time = creation_time

        creation_time_args = dict(
            y=creation_time.year,
            mon=creation_time.month,
            d=creation_time.day,
            h=creation_time.hour,
            min_=creation_time.minute,
            s=creation_time.second,
        )

        empty_kppy_db.create_entry(
            group=root_group,
            title='title_example', comment='comment_example',
            url='example.com', username='john', password='bond',
            **creation_time_args)

        empty_kppy_db.create_entry(
            group=root_group,
            title='title_google', comment='comment_google',
            url='google.com', username='john', password='james',
            **creation_time_args)

        empty_kppy_db.create_entry(
            group=root_group,
            title='title_example', comment='comment_example',
            url='example.com', username='daniel', password='007',
            **creation_time_args)

        assert empty_kppy_db.create_group(title='group1', parent=root_group,
                                          **creation_time_args)
        group1 = None
        for g in empty_kppy_db.groups:
            assert isinstance(g, v1Group)
            if g.title == 'group1' and g.parent is root_group:
                group1 = g
                break
        assert group1

        empty_kppy_db.create_entry(
            group=group1,
            title='title_example', comment='comment_example',
            url='example.com', username='john', password='bond',
            **creation_time_args)

        empty_kppy_db.create_entry(
            group=group1,
            title='title_google', comment='comment_google',
            url='google.com', username='john', password='james',
            **creation_time_args)

        empty_kppy_db.create_entry(
            group=group1,
            title='title_example', comment='comment_example',
            url='example.com', username='daniel', password='007',
            **creation_time_args)

        assert empty_kppy_db.save()
        return empty_kppy_db

    def test_works_to_import(self, mocker, kppy_db):
        mocker.patch.object(kppy_importer.click, 'prompt',
                            return_value=kppy_db.password)

        kppy_db_filepath = py.path.local(kppy_db.filepath)

        importer = kppy_importer.KppyImporter()
        assert importer.match(str(kppy_db_filepath))

        credentials = importer.handle(str(kppy_db_filepath))
        assert credentials == [
            {
                'comment': u'comment_example',
                'name': u'Internet/example.com',
                'modified': kppy_db.mock_creation_time,
                'login': u'john', 'password': u'bond',
                'fullname': 'john@Internet/example.com',
            },  {
                'comment': u'comment_google',
                'name': u'Internet/google.com',
                'modified': kppy_db.mock_creation_time,
                'login': u'john', 'password': u'james',
                'fullname': 'john@Internet/google.com',
            },  {
                'comment': u'comment_example',
                'name': u'Internet/example.com',
                'modified': kppy_db.mock_creation_time,
                'login': u'daniel', 'password': u'007',
                'fullname': 'daniel@Internet/example.com',
            },  {
                'comment': u'comment_example',
                'name': u'Internet/group1/example.com',
                'modified': kppy_db.mock_creation_time,
                'login': u'john', 'password': u'bond',
                'fullname': 'john@Internet/group1/example.com',
            },  {
                'comment': u'comment_google',
                'name': u'Internet/group1/google.com',
                'modified': kppy_db.mock_creation_time,
                'login': u'john', 'password': u'james',
                'fullname': 'john@Internet/group1/google.com',
            },  {
                'comment': u'comment_example',
                'name': u'Internet/group1/example.com',
                'modified': kppy_db.mock_creation_time,
                'login': u'daniel', 'password': u'007',
                'fullname': 'daniel@Internet/group1/example.com',
            }
        ]

    def test_returns_empty_collection_if_passed_a_corrupt_file(self, mocker, tmpdir):
        mocker.patch.object(
            kppy_importer.click, 'prompt', return_value='fake_pass')

        bad_kdb = tmpdir.join('bad.kdb')
        with open(str(bad_kdb), 'wb') as f:
            f.write('bad_db')

        importer = kppy_importer.KppyImporter()
        importer.log = Mock()

        assert importer.match(str(bad_kdb))

        credentials = importer.handle(str(bad_kdb))
        assert importer.log.called
        assert credentials == []
