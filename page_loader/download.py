"""
Главный модуль утилиты.

Для вклчения логирования нужно добавить переменную окржения:
PAGE_LOADER_LOG=уровень_логирования ('debug', 'info', 'warning', 'error').
PAGE_LOADER_LOG_DESTINATION=file если определена как, то лог сохраняется в
файл иначе stdout
"""
import logging
import sys
from os import getcwd, mkdir
from os.path import abspath, exists, join
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from progress.bar import Bar

logger = logging.getLogger(__name__)

err_handler = logging.StreamHandler()
err_handler.setLevel(logging.ERROR)
logger.addHandler(err_handler)

stdin_handler = logging.StreamHandler(sys.stdin)
stdin_handler.setLevel(logging.INFO)
logger.addHandler(stdin_handler)


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

    count = len(soup.find_all(attr[0]))
    progress_bar = Bar(f'Обработка тега {attr[0]}: ', max=count)

    for tag in soup.find_all(attr[0]):
        link = tag.get(attr[1])
        if link is None:
            continue
        if 'http' in link:
            continue

        ext = link.split('.')[-1]
        if link[0] == '/':
            file_name = f'{urlparse(page).netloc}{link}'
        else:
            file_name = f'{urlparse(page).netloc}{urlparse(page).path}/{link}'

        # получения ресурса
        try:
            rsc = requests.get(f'{urlparse(page).scheme}://{file_name}')
        except requests.RequestException:
            logger.error(f'Ресурс {file_name} не доступен.')
            continue
        if rsc.status_code != requests.codes.ok:
            logger.error(
                f"""Сайт вернул, код ошибки {rsc.status_code}.
                Ресурс {file_name} не доступен.""",  # noqa: WPS318
            )
            continue
        file_name = link_to_filename(
            file_name[0:file_name.rfind(ext)],  # noqa: WPS349
        )
        logging.info(f'Ресурс {file_name} получен.')

        file_name = f'{file_name}.{ext}'
        file_name = join(path, file_name)

        # сохранение файла с ресурсом
        try:
            with open(file_name, 'wb') as img:
                img.write(rsc.content)
        except OSError:
            logging.info(f'Не удалось сохранить файл {file_name}.')
        else:
            logging.info(f'Ресурс {file_name} сохранен в файл.')

        # изменение ссылки на ресурс
        tag[attr[1]] = file_name

        progress_bar.next()  # noqa: B305

    progress_bar.finish()

    return soup.prettify()


def download(page, dir_path):  # noqa: WPS210, C901, WPS213
    """
    Загрузка и сохранение сайта.

    :param page: Адрес сайта.
    :param dir_path: Директория для сохранения сайта.
    :return: Полный путь к сохраненному сайту.
    """
    if not dir_path:
        dir_path = getcwd()
    elif not exists(dir_path):
        logger.error(f'Директории {dir_path} не существует.')
        raise FileNotFoundError(f'Директории {dir_path} не существует.')
    logging.info('Проверка наличия папки пройдена.')

    if 'http' not in page:
        logger.error('Неполный адрес сайта.')
        raise ValueError('Неполный адрес сайта.')
    logging.info('Проверка адреса сайта пройдена.')

    try:
        resp = requests.get(page)
    except requests.RequestException:
        raise ConnectionError('Ошибка подключения.')
    if resp.status_code != requests.codes.ok:
        logger.error('Сайт не доступен.')
        raise ConnectionError('Сайт не доступен.')
    logging.info('Проверка доступности сайта пройдена.')

    file_name = link_to_filename(page)

    # Сохранение страницы.
    page_name = f'{file_name}.html'
    page_name = join(dir_path, page_name)
    text_html = resp.text
    try:
        with open(page_name, 'w') as html_file:
            html_file.write(text_html)
    except OSError:
        logger.error('Не удалось сохранить сайт.')
        raise OSError('Не удалось сохранить сайт.')
    logging.info('Страница сайта сохранена.')

    # Поиск и сохранение ресурсов.
    src_dir = join(dir_path, f'{file_name}_files')
    if not exists(src_dir):
        try:
            mkdir(src_dir)
        except OSError:
            logger.error('Не удалось создать папку для ресурсов.')
            raise OSError('Не удалось создать папку для ресурсов.')
    attr = [
        ('img', 'src'),
        ('link', 'href'),
        ('script', 'src'),
    ]
    for tag_arg in attr:
        text_html = download_and_replace(tag_arg, src_dir, text_html, page)
        logging.info(f'Сохранен {tag_arg}.')

    try:
        with open(page_name, 'w') as html_file:  # noqa: WPS440
            html_file.write(text_html)
    except OSError:
        logger.error('Не удалось сохранить изменение ссылок на ресурсы.')
        raise OSError('Не удалось сохранить изменение ссылок на ресурсы.')
    logging.info('Ссылки на ресурсы страницы изменены.')

    return abspath(page_name)
