from os import listdir
from os.path import exists, join
from tempfile import TemporaryDirectory

import requests_mock
from page_loader import download


def test_function_download():  # noqa: WPS210
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
    file_name = 'tests/fixtures/very_long_and_complicated_site_name.html'

    with open(file_name, 'r') as test_page:
        text_html = test_page.read()
    with open('tests//fixtures//img//python.jpeg', 'rb') as test_page:  # noqa: WPS440
        img1_content = test_page.read()
    with open('tests//fixtures//img//python_real.svg', 'rb') as test_page:  # noqa: WPS440
        img2_content = test_page.read()

    with TemporaryDirectory() as temp_dir:
        expected_path = join(temp_dir, correct_file_name)
        with requests_mock.Mocker() as mock:
            mock.get(addres_page, text=text_html)
            mock.get(addres_img1, content=img1_content)
            mock.get(addres_img2, content=img2_content)
            received_patch = download(addres_page, temp_dir)
        if exists(received_patch) and exists(join(temp_dir, correct_dir_name)):
            indicator = True

        list_file = listdir(join(temp_dir, correct_dir_name))

    current_file_name = received_patch.split('/')[-1]

    assert expected_path == received_patch
    assert indicator
    assert correct_file_name == current_file_name
    assert len(list_file) == 2
