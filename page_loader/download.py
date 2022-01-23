"""Главный модуль утилиты"""
from os import getcwd, mkdir
from os.path import abspath, exists, join
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


def link_to_filename(page):
    """
    Преобразовавыет страницу в название.

    :param page: страница сайта .
    :return: преобразованное имя файла.
    """
    file_name = page.split('//')[-1]
    alpha_num = set(
        'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890',
    )
    file_name = [char if char in alpha_num else '-' for char in file_name]
    return ''.join(file_name)


def download_and_replace(attr, path, text_html, page):  # noqa: WPS210
    """
    Загрузка ресурсов.

    Загрузка ресурсов этой страницы и сохранение их в директории path.
    Возвращает измененный text_html.

    :param page: адрес страницы
    :param attr: кортеж с тегом и параметром
    :param path: директория для сохранения
    :param text_html: html-страница
    :return: изменненная страница
    """
    soup = BeautifulSoup(text_html, 'html.parser')
    # проверить куда она ведет
    # скачать ресурс
    # сохранить в нужно папке
    # изменить href.

    for tag in soup.find_all(attr[0]):
        link = tag.get(attr[1])
        if 'http' in link:
            continue
        ext = link.split('.')[-1]
        file_name = f'{urlparse(page).netloc}/{link}'
        rsc = requests.get(urlunparse([  # noqa: WPS317
            urlparse(page).scheme,
            file_name, '', '', '', '',  # noqa: WPS319
        ]))
        file_name = link_to_filename(
            file_name[0:file_name.rfind(ext)],  # noqa: WPS349
        ) + ext
        file_name = join(path, file_name)
        with open(file_name, 'wb') as img:
            img.write(rsc.content)
        tag[attr[1]] = file_name

    return soup.prettify()


def download(page, dir_path):  # noqa: WPS210
    """
    Загрузка и сохранение сайта.

    :param page: Адрес сайта.
    :param dir_path: Директория для сохранения сайта.
    :return: Полный путь к сохраненному сайту.
    """
    if not dir_path:
        dir_path = getcwd()
    elif not exists(dir_path):
        return 'Указанного пути не существует.'

    if 'http' not in page:
        return 'Не полный адрес сайта'

    resp = requests.get(page)
    if resp.status_code != requests.codes.ok:
        return 'Сайт не доступен.'

    file_name = link_to_filename(page)

    # Сохранение страницы.
    page_name = f'{file_name}.html'
    page_name = join(dir_path, page_name)
    text_html = resp.text
    with open(page_name, 'w') as html_file:
        html_file.write(text_html)

    # Поиск и сохранение ресурсов.
    src_dir = join(dir_path, f'{file_name}_files')
    if not exists(src_dir):
        mkdir(src_dir)
    attr = [
        ('img', 'src'),
    ]
    text_html = download_and_replace(attr[0], src_dir, text_html, page)

    with open(page_name, 'w') as html_file:  # noqa: WPS440
        html_file.write(text_html)

    return abspath(page_name)
