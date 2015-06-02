try:
    from mock import MagicMock
except:
    from unittest.mock import MagicMock

from passpie.history import ensure_git, Git


def test_ensure_git_logs_debug_for_git_not_installed(mocker):
    mocker.patch('passpie.history.which', return_value=None)
    mock_logging = mocker.patch('passpie.history.logging')

    @ensure_git()
    def func():
        pass
    result = func()

    assert mock_logging.debug.called
    assert result is None


def test_ensure_returns_specified_return_value_when_exception(mocker):
    mocker.patch('passpie.history.which', return_value=None)
    mock_logging = mocker.patch('passpie.history.logging')
    return_value = 'return value'

    @ensure_git(return_value=return_value)
    def func():
        raise Exception()
    result = func()

    assert result == return_value
    assert mock_logging.debug.called


def test_git_init_creates_a_repo_on_path_commiting_with_message(mocker):
    MockRepo = mocker.patch('passpie.history.Repo')
    path = 'some_path'
    message = 'Initial commit'

    git = Git(path)
    git.init(message=message)

    assert MockRepo.init.called
    MockRepo.init.assert_called_once_with(path)
    MockRepo.init().git.add.assert_called_once_with(all=True)
    MockRepo.init().index.commit.assert_called_once_with(message)


def test_git_commit_creates_commit_with_message(mocker):
    MockRepo = mocker.patch('passpie.history.Repo')
    path = 'some_path'
    message = 'Initial commit'

    git = Git(path)
    git.commit(message)

    MockRepo().git.add.assert_called_once_with(all=True)
    MockRepo().index.commit.assert_called_once_with(message)


def test_git_commit_list_has_expected_reversed_commits_with_index(mocker):
    MockRepo = mocker.patch('passpie.history.Repo')
    mock_repo = MockRepo()
    commits = [
        'another commit',
        'initial commit'
    ]
    mock_repo.iter_commits.return_value = commits
    path = 'some_path'

    git = Git(path)
    commit_list = git.commit_list()

    assert len(commit_list) == len(commits)
    assert [i for i, _ in commit_list] == list(reversed(list(range(len(commits)))))


def test_commit_by_index_returns_none_when_index_not_found(mocker):
    MockRepo = mocker.patch('passpie.history.Repo')
    mock_repo = MockRepo()
    commits = []
    mock_repo.iter_commits.return_value = commits
    index = len(commits) + 1

    git = Git('path')
    commit = git.commit_by_index(index)

    assert commit is None


def test_commit_by_index_returns_found_commit_when_index_exists(mocker):
    MockRepo = mocker.patch('passpie.history.Repo')
    mock_repo = MockRepo()
    commits = ['initial commit']
    mock_repo.iter_commits.return_value = commits
    index = 0

    git = Git('path')
    commit = git.commit_by_index(index)

    assert commit == commits[0]


def test_reset_doesnt_call_git_reset_hard_on_commit_when_not_found(mocker):
    MockRepo = mocker.patch('passpie.history.Repo')
    mock_repo = MockRepo()
    commits = []
    mock_repo.iter_commits.return_value = commits
    index = len(commits) + 1

    git = Git('path')
    commit = git.reset(index)

    assert mock_repo.git.reset.called is False


def test_reset_call_git_reset_hard_on_commit_when_found(mocker):
    MockRepo = mocker.patch('passpie.history.Repo')
    mock_repo = MockRepo()
    commits = [MagicMock()]
    mock_repo.iter_commits.return_value = commits
    index = 0

    git = Git('path')
    commit = git.reset(index)

    assert mock_repo.git.reset.called is True
    mock_repo.git.reset.assert_called_once_with('--hard', commits[0].hexsha)
