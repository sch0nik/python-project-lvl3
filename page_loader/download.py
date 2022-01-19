"""Главный модуль утилиты"""
from os import getcwd
from os.path import abspath, exists, join

import requests


def page_to_filename(page):
    """
    Преобразовавыет страницу в название файла.

    :param page: страница сайта .
    :return: преобразованное имя файла.
    """
    file_name = page.split('//')[-1]
    alpha_num = set(
        'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890',
    )
    file_name = [char if char in alpha_num else '-' for char in file_name]
    file_name = ''.join(file_name)
    return f'{file_name}.html'


def download(page, dir_patch):
    """
    Загрузка и сохранение сайта.

    :param page: Адрес сайта.
    :param dir_patch: Директория для сохранения сайта.
    :return: Полный путь к сохраненному сайту.
    """
    if not dir_patch:
        dir_patch = getcwd()
    elif not exists(dir_patch):
        return 'Указанного пути не существует.'

    if 'http' not in page:
        return 'Не полный адрес сайта'

    resp = requests.get(page)
    if resp.status_code != requests.codes.ok:
        return 'Сайт не доступен.'

    file_name = page_to_filename(page)
    file_name = join(dir_patch, file_name)
    with open(file_name, 'w') as html_file:
        html_file.write(resp.text)

    return abspath(file_name)
