from os.path import exists, join
from tempfile import TemporaryDirectory

import requests_mock
from page_loader import download


def test_function_download():  # noqa: WPS210
    """
    Тест:
        - возвращаемый путь,
        - наличие файлов,
        - правильность наименования.
    Если был получен путь к файлу, значит было обращение к искусственной
    странице.
    """
    file_indicator = False
    page = 'very_long_and_complicated_site_name'
    correct_name = 'www-very-long-and-complicated-site-name-com.html'
    addres_page = f'https://www.{page}.com'
    file_name = f'tests/fixtures/{page}.html'

    with open(file_name, 'r') as test_html:
        text_html = test_html.read()

    with TemporaryDirectory() as temp_dir:
        expected_patch = join(temp_dir, correct_name)
        with requests_mock.Mocker() as mock:
            mock.get(addres_page, text=text_html)
            received_patch = download(addres_page, temp_dir)
        if exists(received_patch):
            file_indicator = True

    current_name = received_patch.split('/')[-1]

    assert expected_patch == received_patch
    assert file_indicator
    assert correct_name == current_name
