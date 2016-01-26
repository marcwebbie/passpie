from passpie.table import Table


def test_table_colorile_calls_click_style_with_key_on_text(mocker):
    mock_click = mocker.patch('passpie.table.click')
    table = Table(headers=['name', 'login'], colors={'red': 'red'})
    table.colorize(key='red', text='text')
    assert mock_click.style.called
    mock_click.style.assert_called_once_with('text', fg=table.colors.get('red'))


def test_render_hide_with_starts_hidden_columns(mocker):
    table = Table(headers=['password'], hidden=['password'])
    mocker.patch('passpie.table.click.style', return_value='password')
    mock_tabulate = mocker.patch('passpie.table.tabulate')
    data = [{'password': 's3cr3t'}, {'password': 'another, s3cr3t'}]

    table.render(data)
    assert mock_tabulate.called
    mock_tabulate.assert_called_once_with([['*****'], ['*****']],
                                          ['password'],
                                          tablefmt=table.table_format,
                                          missingval=table.missing,
                                          numalign='left')



def test_render_colorize_expected_columns(mocker):
    colors = {'name': 'red', 'login': 'blue'}
    table = Table(headers=['name', 'login'], colors=colors)
    mock_tabulate = mocker.patch('passpie.table.tabulate')
    mocker.patch.object(table, 'colorize', return_value='colorized')
    mocker.patch('passpie.table.click.style', return_value='header')
    data = [{'login': 'foo', 'name': 'example.com'}]
    rows = [
        ['colorized', 'colorized']
    ]

    table.render(data)
    assert mock_tabulate.called
    assert table.colorize.called
    table.colorize.assert_any_call('name', 'example.com')
    table.colorize.assert_any_call('login', 'foo')
    mock_tabulate.assert_called_once_with(rows,
                                          ['header', 'header'],
                                          tablefmt=table.table_format,
                                          missingval=table.missing,
                                          numalign='left')
