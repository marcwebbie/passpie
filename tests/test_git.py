import random

import pytest
from passpie.cli import Repo, clone, parse_remote


def test_git_init_creates_a_repository_on_path(mocker, mock_run):
    path = 'some_path'
    cmd = ['git', 'init']
    repo = Repo(path)
    repo.init()

    mock_run.assert_called_once_with(cmd, cwd=path)


def test_git_clone_calls_expected_command_with_repository_url(mocker, mock_run):
    mock_tempdir = mocker.patch('passpie.cli.mkdtemp', return_value='tempdir')
    dest = 'tempdir'
    url = 'https://foo@example.com/user/repo.git'
    cmd = ['git', 'clone', url, dest]
    clone(url)

    assert mock_tempdir.called
    mock_run.assert_called_once_with(cmd)


def test_git_clone_calls_expected_command_with_repository_url_and_destination(mocker, mock_run):
    mock_tempdir = mocker.patch('passpie.cli.mkdtemp', return_value='tempdir')
    url = 'https://foo@example.com/user/repo.git'
    dest = "some/path"
    cmd = ['git', 'clone', url, dest]
    clone(url, dest)

    assert not mock_tempdir.called
    mock_run.assert_called_once_with(cmd)


def test_git_clone_calls_expected_command_with_repository_url_and_depth(mocker, mock_run):
    mock_tempdir = mocker.patch('passpie.cli.mkdtemp', return_value='tempdir')
    url = 'https://foo@example.com/user/repo.git'
    dest = "some/path"
    cmd = ['git', 'clone', url, dest, "--depth", 1]
    clone(url, dest, depth=1)

    assert not mock_tempdir.called
    mock_run.assert_called_once_with(cmd)


def test_git_push_calls_expected_command(mocker, mock_run):
    cmd = ['git', 'push', 'origin', 'master']
    repo = Repo('path')
    repo.push()

    mock_run.assert_called_once_with(cmd, cwd=repo.path)


def test_git_push_calls_expected_command_when_remote_branch_is_passed(mocker, mock_run):
    cmd = ['git', 'push', 'another_origin', 'another_branch']
    repo = Repo('path')
    repo.push(remote='another_origin', branch='another_branch')

    mock_run.assert_called_once_with(cmd, cwd=repo.path)


def test_git_commit_creates_commit_with_message(mocker, mock_run):
    message = 'Initial commit'
    cmd = ['git', 'commit', '-m', message]
    repo = Repo('path')
    repo.commit(message)

    call_to_add = ((['git', 'add', '.'],), {'cwd': 'path'})
    call_to_commit = ((['git', 'commit', '-m', message],), {'cwd': 'path'})
    assert mock_run.call_args_list[0] == call_to_add
    assert mock_run.call_args_list[1] == call_to_commit


def test_parse_remote_returns_tuple():
    result = parse_remote("origin/master")
    assert type(result) == tuple
    assert len(result) == 2


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
