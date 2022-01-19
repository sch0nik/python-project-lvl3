"""
Утилита командной строки для скачивания сайтов. Либо в текущую директорию,
либо в указанную через параметр -о или --output.
"""
import os.path
import requests


def page_to_filename(page):
    file_name = page.split('//')[-1]
    alpha_num = set(
        'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890',
    )
    file_name = [char if char in alpha_num else '-' for char in file_name]
    file_name = ''.join(file_name)
    file_name = f'{file_name}.html'
    return file_name


def download(page, dir_patch):
    """
    Загрузка и сохранение сайта.

    :param page: Адрес сайта.
    :param dir_patch: Директория для сохранения сайта.
    :return: Полный путь к сохраненному сайту.
    """

    if not dir_patch:
        dir_patch = os.getcwd()
    elif not os.path.exists(dir_patch):
        return 'Указанного пути не существует.'

    if 'http' not in page:
        return 'Не полный адрес сайта'

    resp = requests.get(page)
    if resp.status_code != requests.codes.ok:
        return 'Сайт не доступен.'

    file_name = page_to_filename(page)
    file_name = os.path.join(dir_patch, file_name)
    with open(file_name, 'w') as html_file:
        html_file.write(resp.text)

    return os.path.abspath(file_name)
