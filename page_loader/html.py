"""Модуль для работы с ресурсами старницы."""
import logging
import string
from os.path import basename
from urllib.parse import urlparse

from bs4 import BeautifulSoup

log = logging.getLogger('page_loader')


def url_to_filename(link):
    """
    Преобразовавыет строки по схеме: новая-строка-по-схеме.

    :param link: страница сайта.
    :return: преобразованное имя файла.
    """
    netloc = urlparse(link).netloc
    path = urlparse(link).path
    if path:
        path = path if path[0] == '/' else f'/{path}'
    file_name = path.split('/')[-1]
    if path and '.' in file_name:
        ext = file_name.split('.')[-1]
        file_name = f'{path[:-(len(ext) + 1)]}'
    else:
        file_name = path
        ext = 'html'
    file_name = f'{netloc}{file_name}' if netloc else f'{file_name[1:]}'
    alpha_num = string.ascii_letters + string.digits
    file_name = [char if char in alpha_num else '-' for char in file_name]
    file_name = ''.join(file_name)
    return f'{file_name}.{ext}'


def prepare_page(base_url, text_html, dir_path):
    """
    Нахожение ресурсов в text_html и изменение ссылки на них.

    :param dir_path: директория для ресурсов
    :param base_url: урл страницы
    :param text_html: html-текст
    :return: измененный html-текст и список ресурсов list_res[
                {
                    'link': 'https://site_name.com',
                    'path': 'dir_files/file_name.png',
                },
                ]
    """
    tags = [
        ('img', 'src'),
        ('link', 'href'),
        ('script', 'src'),
    ]
    page = urlparse(base_url)
    soup = BeautifulSoup(text_html, 'html.parser')

    list_res = []
    for tag in tags:
        for element in soup.find_all(tag[0]):
            log.debug(f'Проверяется: {element}')
            url = element.attrs.get(tag[1])

            if url is None:
                continue
            url = urlparse(url)
            if url.netloc != page.netloc and url.netloc != '':  # noqa: WPS514
                log.debug('Ссылка на другой домен.')
                continue

            # ссылка для скачивания ресурса
            url = f'{page.scheme}://{page.netloc}{url.path}'
            file_name = url_to_filename(url)

            # Сылка на файл в html-странице
            element[tag[1]] = f'{basename(dir_path)}/{file_name}'

            list_res.append(
                {
                    'link': url,
                    'path': element[tag[1]],
                },
            )
        log.info(f'Список тегов - {tag[0]} составлен.')
    return list_res, soup.prettify()
