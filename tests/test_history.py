import pytest
from passpie.history import ensure_git, Repository


@pytest.fixture
def mock_process(mocker):
    return mocker.patch('passpie.history.process')


def test_ensure_git_logs_debug_for_git_not_installed(mocker, mock_process):
    mocker.patch('passpie.history.which', return_value=None)
    mock_logging = mocker.patch('passpie.history.logging')

    @ensure_git()
    def func():
        pass
    result = func()

    assert mock_logging.debug.called
    assert result is None


def test_ensure_returns_specified_return_value_when_exception(mocker, mock_process):
    mocker.patch('passpie.history.which', return_value='/usr/bin/gpg')
    mock_logging = mocker.patch('passpie.history.logging')
    return_value = 'return value'

    @ensure_git(return_value=return_value)
    def func():
        raise ValueError()
    result = func()

    assert result == return_value
    assert mock_logging.debug.called


def test_git_init_creates_a_repository_on_path(mocker, mock_process):
    path = 'some_path'
    cmd = ['git', 'init', path]
    repo = Repository(path)
    repo.init()

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_commit_creates_commit_with_message(mocker, mock_process):
    path = 'some_path'
    message = 'Initial commit'
    cmd = ['git', 'commit', '-m', message]
    repo = Repository(path)
    mocker.patch.object(repo, 'add')

    repo.commit(message)

    repo.add.assert_called_once_with(all=True)
    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_commit_list_has_expected_commit_list(mocker, mock_process):
    commit_list = [
        'another commit',
        'initial commit'
    ]
    mock_process.call.return_value = ("\n".join(commit_list), 'no error')
    path = 'some_path'
    cmd = ['git', 'log', '--reverse', '--pretty=format:%s']
    repo = Repository(path)
    commits = repo.commit_list()

    assert len(repo.commit_list()) == len(commits)
    mock_process.call.assert_any_call(cmd, cwd=repo.path)


def test_reset_doesnt_call_git_reset_hard_on_commit_when_not_found(mocker, mock_process):
    sha_list = []
    index = 0

    repo = Repository('path')
    mocker.patch.object(repo, 'sha_list', return_value=sha_list)
    repo.reset(index)

    mock_process.call.called is False


def test_reset_call_git_reset_hard_on_commit_when_found(mocker, mock_process):
    sha_list = [
        'd6b52b5',
        '34c5439',
        '5910c2b',
    ]
    index = 0
    cmd = ['git', 'reset', '--hard', sha_list[index]]

    repo = Repository('path')
    mocker.patch.object(repo, 'sha_list', return_value=sha_list)
    repo.reset(index)

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)
