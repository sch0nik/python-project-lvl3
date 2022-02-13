from os import listdir
from os.path import exists, join
from tempfile import TemporaryDirectory

import pytest
import requests_mock

from page_loader import download
from page_loader.html import url_to_filename

correct_file_name = 'www-site-name-com.html'
correct_dir_name = 'www-site-name-com_files'
addres_page = 'https://www.site_name.com'
addres_img1 = f'{addres_page}/img/python.jpeg'
addres_img2 = f'{addres_page}/img/python_real.svg'
addres_style = f'{addres_page}/files/css/style.css'
addres_js = f'{addres_page}/empty.js'
file_name = 'tests/fixtures/very_long_and_complicated_site_name.html'


# def mock_page_download(
#         dir_path,
#         text_html,
#         img1_content,
#         img2_content,
#         css_content,
#         js_content,
# ):
head_txt = {'Content-Type': 'text/html'}
head_all = {'Content-Type': 'all'}

# return received_patch


def test_page_loader_download(
        text_html,
        img1_content,
        img2_content,
        css_content,
        js_content
):  # noqa: WPS210
    """
    Тест:
        - возвращаемый путь,
        - наличие файла html и директории с ресурсами,
        - правильность наименования.
    """
    indicator = False

    with TemporaryDirectory() as temp_dir:
        expected_path = join(temp_dir, correct_file_name)
        with requests_mock.Mocker() as mock:
            mock.get(addres_page, text=text_html, headers=head_txt)
            mock.get(addres_img1, content=img1_content, headers=head_all)
            mock.get(addres_img2, content=img2_content, headers=head_all)
            mock.get(addres_style, content=css_content, headers=head_all)
            mock.get(addres_js, content=js_content, headers=head_all)
            received_patch = download(addres_page, temp_dir)
        if exists(received_patch) and exists(join(temp_dir, correct_dir_name)):
            indicator = True

    current_file_name = received_patch.split('/')[-1]

    assert expected_path == received_patch
    assert indicator
    assert correct_file_name == current_file_name


def test_page_loader_files(
        text_html,
        img1_content,
        img2_content,
        css_content,
        js_content
):  # noqa: WPS210
    """
    Тест:
        - проверка правильности содержимого всех файлов
        - верное количество файлов
    """

    with open('tests/fixtures/expected.html', 'r') as exp_file:
        expected = exp_file.read()

    with TemporaryDirectory() as temp_dir:
        with requests_mock.Mocker() as mock:
            mock.get(addres_page, text=text_html, headers=head_txt)
            mock.get(addres_img1, content=img1_content, headers=head_all)
            mock.get(addres_img2, content=img2_content, headers=head_all)
            mock.get(addres_style, content=css_content, headers=head_all)
            mock.get(addres_js, content=js_content, headers=head_all)
            received_patch = download(addres_page, temp_dir)
        with open(received_patch, 'r') as file_html:
            received = file_html.read()

        path = join(temp_dir, correct_dir_name)
        list_file = listdir(path)
        list_content = {img1_content, img2_content, css_content, js_content}
        exp_list_content = set()
        for item in list_file:
            with open(join(path, item), 'rb') as f:
                exp_list_content.add(f.read())

    assert len(list_file) == 4
    assert expected == received
    assert exp_list_content == list_content


def test_page_loader_exceptions():
    """Тестирование исключений."""
    with TemporaryDirectory() as temp_dir:
        with pytest.raises(FileNotFoundError):
            download('https://google.com', 'Непонятная_папка')

        with pytest.raises(ValueError):
            download('Непонятный_сайт.', temp_dir)

        with pytest.raises(ConnectionError):
            with requests_mock.Mocker() as mock:
                mock.get('https://google.com', status_code=404)
                download('https://google.com', temp_dir)


def test_page_loader_link_to_filename():
    """Проверка формирования имени ссылки."""
    list_link = [
        'https://site.com',
        'https://site.com/asdf/fer',
        'https://site.com/asdf/fer.png',
        '/site/asdf/fer.png',
        'site/asdf/fer',
    ]
    expected_list_link = [
        'site-com.html',
        'site-com-asdf-fer.html',
        'site-com-asdf-fer.png',
        'site-asdf-fer.png',
        'site-asdf-fer.html',
    ]
    for index, link in enumerate(expected_list_link):
        assert url_to_filename(list_link[index]) == link, list_link[index]
