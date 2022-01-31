from os import listdir
from os.path import exists, join
from tempfile import TemporaryDirectory

import pytest
import requests_mock

from page_loader import download


def test_download():  # noqa: WPS210
    """
    Тест:
        - возвращаемый путь,
        - наличие файла html и директории,
        - правильность наименования.
        - наличие 2 изображений в этой директории
          (на тестовой странице ссылки на 3 изображения),
        - проверка правильности ссылки на ресурс внутри страницы,
    Если был получен путь к файлу, значит было обращение к искусственной
    странице.
    """
    indicator = False
    correct_file_name = 'www-very-long-and-complicated-site-name-com.html'
    correct_dir_name = 'www-very-long-and-complicated-site-name-com_files'
    addres_page = 'https://www.very_long_and_complicated_site_name.com'
    addres_img1 = f'{addres_page}/img/python.jpeg'
    addres_img2 = f'{addres_page}/img/python_real.svg'
    addres_style = f'{addres_page}/style.css'
    addres_js = f'{addres_page}/empty.js'
    file_name = 'tests/fixtures/very_long_and_complicated_site_name.html'

    with open(file_name, 'r') as test_page:
        text_html = test_page.read()
    with open('tests//fixtures//img//python.jpeg', 'rb') as test_page:  # noqa: WPS440
        img1_content = test_page.read()
    with open('tests//fixtures//img//python_real.svg', 'rb') as test_page:  # noqa: WPS440
        img2_content = test_page.read()
    with open('tests//fixtures//style.css', 'r') as test_page:  # noqa: WPS440
        css_content = test_page.read()
    with open('tests//fixtures//empty.js', 'r') as test_page:  # noqa: WPS440
        js_content = test_page.read()

    with TemporaryDirectory() as temp_dir:
        expected_path = join(temp_dir, correct_file_name)
        with requests_mock.Mocker() as mock:
            mock.get(addres_page, text=text_html)
            mock.get(addres_img1, content=img1_content)
            mock.get(addres_img2, content=img2_content)
            mock.get(addres_style, text=css_content)
            mock.get(addres_js, text=js_content)
            try:
                received_patch = download(addres_page, temp_dir)
            except requests_mock.exceptions.NoMockAddress as exc:
                received_patch = ''
        if exists(received_patch) and exists(join(temp_dir, correct_dir_name)):
            indicator = True

        list_file = listdir(join(temp_dir, correct_dir_name))

    current_file_name = received_patch.split('/')[-1]

    assert expected_path == received_patch, exc
    assert indicator
    assert correct_file_name == current_file_name
    assert len(list_file) == 4


def test_link():  # noqa: WPS210
    """
    Тест:
        - проверка правильности ссылки на ресурс внутри страницы,
    """
    addres_page = 'https://www.very_long_and_complicated_site_name.com'
    addres_img1 = f'{addres_page}/img/python.jpeg'
    addres_img2 = f'{addres_page}/img/python_real.svg'
    addres_css = f'{addres_page}/style.css'
    addres_js = f'{addres_page}/empty.js'
    file_name = 'tests/fixtures/very_long_and_complicated_site_name.html'

    with open(file_name, 'r') as test_page:
        text_html = test_page.read()
    with open('tests//fixtures//img//python.jpeg', 'rb') as test_page:  # noqa: WPS440
        img1_content = test_page.read()
    with open('tests//fixtures//img//python_real.svg', 'rb') as test_page:  # noqa: WPS440
        img2_content = test_page.read()
    with open('tests//fixtures//style.css', 'r') as test_page:  # noqa: WPS440
        css_content = test_page.read()
    with open('tests//fixtures//empty.js', 'r') as test_page:  # noqa: WPS440
        js_content = test_page.read()
    link_res = [
        'www-very-long-and-complicated-site-name-com_files/style.css',
        'www-very-long-and-complicated-site-name-com_files/python_real.svg',
        'www-very-long-and-complicated-site-name-com_files/python.jpeg',
        'www-very-long-and-complicated-site-name-com_files/empty.js',
    ]

    with TemporaryDirectory() as temp_dir:
        with requests_mock.Mocker() as mock:
            mock.get(addres_page, text=text_html)
            mock.get(addres_img1, content=img1_content)
            mock.get(addres_img2, content=img2_content)
            mock.get(addres_css, text=css_content)
            mock.get(addres_js, text=js_content)
            received_patch = download(addres_page, temp_dir)
        with open(received_patch, 'r') as file_html:
            received_html = file_html.read()

        link_res = [True for link in link_res if link in received_html]

    assert all(link_res)


def test_exception():
    with TemporaryDirectory() as temp_dir:
        with pytest.raises(FileNotFoundError):
            download('Непонятный_сайт.', 'Непонятная_папка')

        with pytest.raises(ValueError):
            download('Непонятный_сайт.', temp_dir)

        with pytest.raises(ConnectionError):
            with requests_mock.Mocker() as mock:
                mock.get('https://google.com', status_code=404)
                download('https://google.com', temp_dir)
