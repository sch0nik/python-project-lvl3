""" Главный модуль утилиты. """
import logging
from os import getcwd
from os.path import abspath, join, exists
from urllib.parse import urlparse

import requests

from progress.bar import Bar

from page_loader.fs import mk_dir, save_file
from page_loader.html import url_to_filename, prepare_page


def get(url):
    """
    Загрузка файла.

    :param url: ссылка на файл
    :return: содержимое файла
    """
    if not urlparse(url).netloc:
        raise ValueError('Неполный адрес.')
    logging.info(f'Проверка адреса {url} пройдена.')

    try:  # noqa: WPS503
        resp = requests.get(url)
    except requests.RequestException as exc:
        logging.info(f'Ошибка подключения {exc}')
        raise ConnectionError(f'Ошибка подключения {exc}')
    if resp.status_code != requests.codes.ok:
        logging.error(f'Ссылка не доступна. {resp.status_code}')
        raise ConnectionError(f'Ссылка не доступна. {resp.status_code}')
    logging.info(f'Файл {url} получен.')
    conn_type = resp.headers.get('Content-Type')
    if conn_type and 'text/html' in conn_type:
        resp.encoding = 'utf-8'
        return resp.text
    else:
        return resp.content


def download(url, directory):  # noqa: WPS210, C901, WPS213
    """
    Загрузка и сохранение сайта.

    :param url: Адрес сайта.
    :param directory: Директория для сохранения сайта.
    :return: Полный путь к сохраненному сайту.
    """
    if not directory:
        directory = getcwd()
    elif not exists(directory):
        raise FileNotFoundError(f'Директории {directory} не существует.')
    logging.info('Проверка наличия папки пройдена.')

    page_name = url_to_filename(url)
    page_name = join(directory, page_name)
    res_dir = f'{page_name[:-5]}_files'

    text_html = get(url)

    logging.debug('Получение списка ссылок на ресурсы')
    urls, text_html = prepare_page(url, text_html, res_dir)

    logging.debug('Сохранение html-файла')
    save_file(page_name, text_html)

    if not urls:
        logging.debug('Ресурсов нет.')
        return abspath(page_name)

    logging.debug('Сохранение списка ресурсов')
    mk_dir(res_dir)
    logging.info(f'Сохранение ресурсов. Всего {len(urls)}')
    progress_bar = Bar('Сохранение: ', max=len(urls))
    for url in urls:
        # Загрузка ресурса
        try:
            res = get(url['link'])
        except ConnectionError as exc:
            logging.debug(f'Ресурс {url} не загружен. {exc}')
            continue
        logging.debug(f'Ресурс {url} загружен.')

        # Сохранение ресурса
        try:
            save_file(join(directory, url['path']), res)
        except OSError:
            logging.info(f'Ресурс {url} не сохранен.')
            progress_bar.next()  # noqa: B305
            continue
        logging.info(f'Ресурс {url} сохранен.')

        progress_bar.next()  # noqa: B305

    progress_bar.finish()

    return abspath(page_name)
