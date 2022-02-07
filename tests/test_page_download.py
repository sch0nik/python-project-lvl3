from os import listdir
from os.path import exists, join
from tempfile import TemporaryDirectory

import pytest
import requests_mock

from page_loader import download
from page_loader.html_processing import link_to_filename

correct_file_name = 'www-site-name-com.html'
correct_dir_name = 'www-site-name-com_files'
addres_page = 'https://www.site_name.com'
addres_img1 = f'{addres_page}/img/python.jpeg'
addres_img2 = f'{addres_page}/img/python_real.svg'
addres_style = f'{addres_page}/files/css/style.css'
addres_js = f'{addres_page}/empty.js'
file_name = 'tests/fixtures/very_long_and_complicated_site_name.html'

with open(file_name, 'r') as test_page:
    text_html = test_page.read()


def mock_page_download(dir_path):
    with requests_mock.Mocker() as mock:
        mock.get(addres_page, text=text_html)
        mock.get(addres_img1, content=b'img1_content')
        mock.get(addres_img2, content=b'img2_content')
        mock.get(addres_style, text='css_content')
        mock.get(addres_js, text='js_content')
        received_patch = download(addres_page, dir_path)
    return received_patch


def test_page_loader():  # noqa: WPS210
    """
    Тест:
        - возвращаемый путь,
        - наличие файла html и директории,
        - правильность наименования.
        - наличие файлов с ресурсами,
    Если был получен путь к файлу, значит было обращение к искусственной
    странице.
    """
    indicator = False

    with TemporaryDirectory() as temp_dir:
        # Ожидаемый путь
        expected_path = join(temp_dir, correct_file_name)
        # Получаем путь
        received_patch = mock_page_download(temp_dir)
        # существует ли файл хтмл и папка с ресурсами,
        # название папки тожее должно быть правильным
        if exists(received_patch) and exists(join(temp_dir, correct_dir_name)):
            indicator = True

        # список файлов в ожидаемой папке с ресурсами
        list_file = listdir(join(temp_dir, correct_dir_name))

    # имя скачанного хтмл-файла
    current_file_name = received_patch.split('/')[-1]

    assert expected_path == received_patch  # Проверка на соответствие пути
    assert indicator  # Проверка наличия файлов
    assert correct_file_name == current_file_name   # Проверка на имени файла
    assert len(list_file) == 4   # Количество скаченных фалов


def test_html():  # noqa: WPS210
    """
    Тест:
        - проверка правильности ссылки на ресурс внутри страницы,
    """

    with open('tests/fixtures/expected.html', 'r') as test_file:
        expected = test_file.read()

    with TemporaryDirectory() as temp_dir:
        # Получаем путь
        received_patch = mock_page_download(temp_dir)
        # получаем содержимое полученного хтмл файла
        with open(received_patch, 'r') as file_html:
            received = file_html.read()

    assert expected == received  # Сравнение хтмл-файлов


def test_exception():
    """Тестирование исключений."""
    with TemporaryDirectory() as temp_dir:
        with pytest.raises(FileNotFoundError):
            download('Непонятный_сайт.', 'Непонятная_папка')

        with pytest.raises(ValueError):
            download('Непонятный_сайт.', temp_dir)

        with pytest.raises(ConnectionError):
            with requests_mock.Mocker() as mock:
                mock.get('https://google.com', status_code=404)
                download('https://google.com', temp_dir)


def test_link_to_filename():
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
        assert link_to_filename(list_link[index]) == link, list_link[index]
