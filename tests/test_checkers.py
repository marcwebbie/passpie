from passpie import checkers
from datetime import datetime, timedelta


def test_repeated_deepcopy_credentials(mocker):
    mock_deepcopy = mocker.patch('passpie.checkers.deepcopy')
    credentials = [{'fullname': 'foo@example.com', 'password': 's3cr3t'}]

    checkers.repeated(credentials, limit=1)
    assert mock_deepcopy.called
    mock_deepcopy.assert_called_once_with(credentials)


def test_modified_sets_credential_modifield_field_none(mocker):
    credentials = [{'modified': datetime(year=2016, month=1, day=1)}]
    expected_credentials = [{'modified': None}]
    mock_datetime = mocker.patch('passpie.checkers.datetime')
    mock_datetime.now.return_value = credentials[0]['modified'] + timedelta(days=1)

    result_credentials = checkers.modified(credentials, days=1)
    assert result_credentials == expected_credentials


def test_modified_sets_credential_modifield_field__with_string_days_count(mocker):
    credentials = [{'modified': datetime(year=2016, month=1, day=1)}]
    expected_credentials = [{'modified': "3 days ago"}]
    mock_datetime = mocker.patch('passpie.checkers.datetime')
    mock_datetime.now.return_value = credentials[0]['modified'] + timedelta(days=3)

    result_credentials = checkers.modified(credentials, days=1)
    assert result_credentials == expected_credentials


def test_modified_deepcopy_credentials(mocker):
    mock_deepcopy = mocker.patch('passpie.checkers.deepcopy')
    credentials = [{'modified': datetime.now()}]

    checkers.modified(credentials, days=1)
    assert mock_deepcopy.called
    mock_deepcopy.assert_called_once_with(credentials)
