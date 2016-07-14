from functools import partial
import random

import pytest
from passpie.git import Repo, clone, parse_remote, ensure_git, safe_join


@pytest.fixture
def mock_run(mocker):
    return mocker.patch('passpie.git.run')


def test_git_init_creates_a_repository_on_path(mocker, mock_run):
    path = 'some_path'
    cmd = ['git', 'init']
    repo = Repo(path)
    repo.init()

    mock_run.assert_called_once_with(cmd, cwd=path)


def test_git_clone_calls_expected_command_with_repository_url(mocker, mock_run):
    mock_tempdir = mocker.patch('passpie.git.mkdtemp', return_value='tempdir')
    dest = 'tempdir'
    url = 'https://foo@example.com/user/repo.git'
    cmd = ['git', 'clone', url, dest]
    clone(url)

    assert mock_tempdir.called
    mock_run.assert_called_once_with(cmd)


def test_git_clone_calls_expected_command_with_repository_url_and_destination(mocker, mock_run):
    mock_tempdir = mocker.patch('passpie.git.mkdtemp', return_value='tempdir')
    url = 'https://foo@example.com/user/repo.git'
    dest = "some/path"
    cmd = ['git', 'clone', url, dest]
    clone(url, dest)

    assert not mock_tempdir.called
    mock_run.assert_called_once_with(cmd)


def test_git_clone_calls_expected_command_with_repository_url_and_depth(mocker, mock_run):
    mock_tempdir = mocker.patch('passpie.git.mkdtemp', return_value='tempdir')
    url = 'https://foo@example.com/user/repo.git'
    dest = "some/path"
    cmd = ['git', 'clone', url, dest, "--depth", 1]
    clone(url, dest, depth=1)

    assert not mock_tempdir.called
    mock_run.assert_called_once_with(cmd)


def test_git_push_calls_expected_command(mocker, mock_run, tempdir_with_git):
    cmd = ['git', 'push', 'origin', 'HEAD']
    repo = Repo(tempdir_with_git)
    repo.push()

    mock_run.assert_called_once_with(cmd, cwd=repo.path)


def test_git_push_calls_expected_command_when_remote_branch_is_passed(mocker, mock_run, tempdir_with_git):
    cmd = ['git', 'push', 'another_origin', 'another_branch']
    repo = Repo(tempdir_with_git)
    repo.push(remote='another_origin', branch='another_branch')

    mock_run.assert_called_once_with(cmd, cwd=repo.path)


def test_git_commit_creates_commit_with_message(mocker, mock_run, tempdir_with_git):
    message = 'Initial commit'
    cmd = ['git', 'commit', '-m', message]
    repo = Repo(tempdir_with_git)
    repo.commit(message)

    mock_run.assert_any_call(
        ["git", "add", "."], cwd=tempdir_with_git)
    mock_run.assert_any_call(
        ["git", "commit", "-m", message], cwd=tempdir_with_git)


def test_parse_remote_returns_tuple():
    result = parse_remote("origin/master")
    assert type(result) == tuple
    assert len(result) == 2
    assert result[0] == "origin"
    assert result[1] == "master"


def test_parse_remote_returns_origin_and_branch_values():
    origin = random.choice(["a", "b", "c"])
    branch = random.choice(["a", "b", "c"])
    remote_string = "%s/%s" % (origin, branch)
    parsed_origin, parsed_branch = parse_remote(remote_string)
    assert origin == parsed_origin
    assert branch == parsed_branch


def test_parse_remote_raises_value_error_exception_when_remote_string_has_more_than_two_slashes():
    with pytest.raises(ValueError):
        result = parse_remote("origin/master/something")
