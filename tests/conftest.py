import pytest


@pytest.fixture
def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


@pytest.fixture
def mck(mocker, mock_open):
    mocker.mock_open = mock_open
    return mocker
