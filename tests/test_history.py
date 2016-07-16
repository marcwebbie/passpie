import pytest
from passpie.history import ensure_git, Repository, clone


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

    assert mock_logging.error.called
    assert result is None


def test_git_init_creates_a_repository_on_path(mocker, mock_process):
    path = 'some_path'
    cmd = ['git', 'init', path]
    repo = Repository(path)
    repo.init()

    mock_process.call.assert_called_once_with(cmd)


def test_calls_pull_rebase_on_initialization_when_autopull_is_passed(mocker, mock_process):
    mocker.patch.object(Repository, 'pull_rebase')
    autopull = ['origin', 'master']
    repo = Repository('path', autopull)
    assert repo.pull_rebase.called
    repo.pull_rebase.assert_called_once_with(*autopull)


def test_git_pull_rebase_calls_expected_command(mocker, mock_process):
    cmd = ['git', 'pull', '--rebase', 'origin', 'master']
    repo = Repository('path')
    repo.pull_rebase()

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_pull_rebase_calls_expected_command_when_remote_branch_is_passed(mocker, mock_process):
    cmd = ['git', 'pull', '--rebase', 'another_origin', 'another_branch']
    repo = Repository('path')
    repo.pull_rebase(remote='another_origin', branch='another_branch')

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_clone_calls_expected_command_with_repository_url(mocker, mock_process):
    mock_tempdir = mocker.patch('passpie.history.tempdir', return_value='tempdir')
    dest = 'tempdir'
    url = 'https://foo@example.com/user/repo.git'
    cmd = ['git', 'clone', url, dest]
    clone(url)

    assert mock_tempdir.called
    mock_process.call.assert_called_once_with(cmd)


def test_git_clone_calls_expected_command_with_repository_url_and_destination(mocker, mock_process):
    mock_tempdir = mocker.patch('passpie.history.tempdir', return_value='tempdir')
    url = 'https://foo@example.com/user/repo.git'
    dest = "some/path"
    cmd = ['git', 'clone', url, dest]
    clone(url, dest)

    assert not mock_tempdir.called
    mock_process.call.assert_called_once_with(cmd)


def test_git_clone_calls_expected_command_with_repository_url_and_depth(mocker, mock_process):
    mock_tempdir = mocker.patch('passpie.history.tempdir', return_value='tempdir')
    url = 'https://foo@example.com/user/repo.git'
    dest = "some/path"
    cmd = ['git', 'clone', url, dest, "--depth", 1]
    clone(url, dest, depth=1)

    assert not mock_tempdir.called
    mock_process.call.assert_called_once_with(cmd)


def test_git_push_calls_expected_command(mocker, mock_process):
    cmd = ['git', 'push', 'origin', 'master']
    repo = Repository('path')
    repo.push()

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_push_calls_expected_command_when_remote_branch_is_passed(mocker, mock_process):
    cmd = ['git', 'push', 'another_origin', 'another_branch']
    repo = Repository('path')
    repo.push(remote='another_origin', branch='another_branch')

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_add_has_call_with_expected_command(mocker, mock_process):
    cmd = ['git', 'add', '.']
    repo = Repository('path')
    repo.add()

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_add_has_call_with_expected_command_with_all_flag_when_all_is_true(mocker, mock_process):
    cmd = ['git', 'add', '--all', '.']
    repo = Repository('path')
    repo.add(all=True)

    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_sha_list_has_call_with_expected_command(mocker, mock_process):
    output = 'a\nb'
    mock_process.call.return_value = (output, '')
    cmd = ['git', 'log', '--reverse', '--pretty=format:%h']
    repo = Repository('path')
    result = repo.sha_list()

    assert result == output.splitlines()
    mock_process.call.assert_called_once_with(cmd, cwd=repo.path)


def test_git_commit_creates_commit_with_message(mocker, mock_process):
    message = 'Initial commit'
    repo = Repository('path')
    mocker.patch.object(repo, 'add')
    cmd = ['git', 'commit', '--author={}'.format(repo.author), '-m', message]

    repo.commit(message)

    repo.add.assert_called_once_with(all=True)
    mock_process.call.assert_any_call(cmd, cwd=repo.path)


def test_git_commit_calls_push_when_autopush_set(mocker, mock_process):
    message = 'Initial commit'
    cmd = ['git', 'commit', '-m', message]
    repo = Repository('path', autopush=['origin', 'master'])
    mocker.patch.object(repo, 'push')

    repo.commit(message)
    assert repo.push.called


def test_git_commit_list_has_expected_commit_list(mocker, mock_process):
    commit_list = [
        'another commit',
        'initial commit'
    ]
    mock_process.call.return_value = ("\n".join(commit_list), 'no error')
    cmd = ['git', 'log', '--reverse', '--pretty=format:%s']
    repo = Repository('path')
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
