"""Модуль для работы с ресурсами старницы."""
import logging
import string
from os.path import basename, join
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from page_loader.fs import save_file
from progress.bar import Bar

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


def page_processing(url, text_html, dir_path):
    """
    Нахожение ресурсов в text_html и изменение ссылки на них.

    :param dir_path: директория для ресурсов
    :param url: урл страницы
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
    page = urlparse(url)
    soup = BeautifulSoup(text_html, 'html.parser')

    # Будущий список ресурсов
    list_res = []
    # Цикл по тегам
    for tag in tags:
        # Цикл по найденному списку данного тега
        for element in soup.find_all(tag[0]):
            log.debug(f'Проверяется: {element}')
            link = element.attrs.get(tag[1])

            # Если ссылки нет, то пропускаем этот элемент
            if link is None:
                continue
            link = urlparse(link)
            # Если ссылка на другой домен, то пропускаем этот элемент
            if link.netloc != page.netloc and link.netloc != '':  # noqa: WPS514
                log.debug('Ссылка на другой домен.')
                continue

            # ссылка для скачивания ресурса
            link = urlunparse((page.scheme, page.netloc, *(link[2:])))
            file_name = url_to_filename(link)

            # Сылка на файл в html-странице
            element[tag[1]] = f'{basename(dir_path)}/{file_name}'

            list_res.append(
                {
                    'link': link,
                    'path': element[tag[1]],
                },
            )
        log.info(f'Список тегов - {tag[0]} составлен.')
    return list_res, soup.prettify()


def save_resources(list_res, dir_path):  # noqa: WPS210
    """
    Сохранение списка ресурсов.

    :param dir_path: директория для сохраненияя ресурсов
    :param list_res: список ресурсов
    :return: None
    """
    log.debug(f'Сохранение ресурсов. Всего {len(list_res)}')
    progress_bar = Bar('Сохранение: ', max=len(list_res))
    for link in list_res:
        # Загрузка ресурса
        res = load_file(link['link'], 'wb', missing=True)
        if res is None:
            continue
        log.debug(f'{link} загружен.')
        # Сохранение ресурса
        if not save_file(join(dir_path, link['path']), res, 'wb'):
            # Если сохранить не получилось,
            # то записываем в лог и продолжаем со следующего
            log.error(f'Ресурс {link} не сохранен.')
            progress_bar.next()  # noqa: B305
            continue
        log.debug(f'Ресурс {link} сохранен.')
        progress_bar.next()  # noqa: B305

    progress_bar.finish()


def load_file(url, mode='w', missing=False):
    """
    Загрузка файла.

    :param url: ссылка на файл
    :param mode: режим w - текстовый файл, wb - бинарный
    :param missing:  если False, то вызывается исключение
    :return: либо содержимое файла, либо None
    """
    if not urlparse(url).netloc:
        raise ValueError('Неполный адрес.')
    log.info('Проверка адреса пройдена.')

    try:  # noqa: WPS503
        resp = requests.get(url)
    except requests.RequestException as exc:
        log.info(f'Ошибка подключения {exc}')
        if not missing:
            raise ConnectionError(f'Ошибка подключения {exc}')
    else:
        if resp.status_code != requests.codes.ok:
            log.error(f'Ссылка не доступна. {resp.status_code}')
            if not missing:
                raise ConnectionError(f'Ссылка не доступна. {resp.status_code}')
        log.info('Проверка доступности ссылки пройдена.')
        return resp.content if mode == 'wb' else resp.text
    return None
