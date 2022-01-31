"""
Главный модуль утилиты.

Сохраняет только ('img', 'src'), ('link', 'href'), ('script', 'src').
Для вклчения логирования нужно добавить переменную окржения:
PAGE_LOADER_LOG=уровень_логирования ('debug', 'info', 'warning', 'error').
"""
import logging
import os.path
import string
import sys
from os import getcwd, mkdir
from os.path import abspath, exists, join, split, basename, isabs
from urllib.parse import urlparse, urlunparse

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


class ParseUrl(object):
    def __init__(self, res):
        self.scheme = res.scheme
        self.netloc = res.netloc
        self.path = res.path
        self.params = res.params
        self.query = res.query
        self.fragment = res.fragment

    def __get__(self, instance, owner):
        return (
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        )

    def __repr__(self):
        return f'ParseUrl(scheme={self.scheme}; netloc={self.netloc}; ' \
               f'path={self.path}; params={self.params}; ' \
               f'query={self.query}; fragment={self.fragment})'


def link_to_filename(line):
    """
    Преобразовавыет строки по схеме: новая-строка-по-схеме.

    :param line: страница сайта.
    :return: преобразованное имя файла.
    """
    file_name = line.split('//')[-1]
    alpha_num = string.ascii_letters + string.digits
    file_name = [char if char in alpha_num else '-' for char in file_name]
    return ''.join(file_name)


def return_path(directory):
    """
    Проверка на существование директории.

    Если директория не указана возвращает текущую.
    Если она не существует, то вызывает исключение.

    :param directory: путь к директории.
    :return: тот же путь или текущий.
    """
    if not directory:
        return getcwd()
    elif not exists(directory):
        logger.error(f'Директории {directory} не существует.')
        raise FileNotFoundError(f'Директории {directory} не существует.')
    logging.info('Проверка наличия папки пройдена.')
    return directory


def load_file(url, mode='w', missing=False):
    if 'http' not in url:
        logger.error('Неполный адрес.')
        raise ValueError('Неполный адрес.')
    logging.info('Проверка адреса пройдена.')

    try:
        resp = requests.get(url)
    except requests.RequestException as exc:
        logger.info(f'Ошибка подключения {exc}')
        if not missing:
            raise ConnectionError(f'Ошибка подключения {exc}')
    else:
        if resp.status_code != requests.codes.ok:
            logger.error(f'Ссылка не доступна. {resp.status_code}')
            if not missing:
                raise ConnectionError(f'Ссылка не доступна. {resp.status_code}')
        logging.info('Проверка доступности ссылки пройдена.')
        return resp.text if mode == 'w' else resp.content
    return None


def save_file(file_name, content, mode='w'):
    try:
        with open(file_name, mode) as res_file:
            res_file.write(content)
    except OSError as exc:
        logger.error(f'Не удалось сохранить файл {file_name}. Ошибка {exc}')
        raise OSError(f'Не удалось сохранить файл {file_name}. Ошибка {exc}')
    logging.info(f'Файл {file_name} сохранен.')


def mk_dir(res_dir):
    if not exists(res_dir):
        try:
            mkdir(res_dir)
        except OSError:
            logger.error('Не удалось создать папку для ресурсов.')
            raise OSError('Не удалось создать папку для ресурсов.')


def find_resource(soup):
    tags = [
        ('img', 'src', 'wb'),
        ('link', 'href', 'w'),
        ('script', 'src', 'w'),
    ]
    list_res = []
    for tag in tags:
        for element in soup.find_all(tag[0]):
            if element.get(tag[1]) is None:
                continue
            list_res.append(
                {
                    'link': ParseUrl(urlparse(element[tag[1]])),
                    'obj': element,
                    'mode': tag[2],
                },
            )
        logger.info(f'Список тегов - {tag[0]} составлен.')
    return list_res


def save_resources(list_res, directory):
    logger.debug(f'Сохранение ресурсов. Всего {len(list_res)}')
    for element in list_res:
        # Ссылка на скачивание
        link = urlunparse((
            element['link'].scheme,
            element['link'].netloc,
            element['link'].path,
            '',
            '',
            '',
        ))
        res = load_file(link, element['mode'], missing=True)
        if res is None:
            continue
        logger.debug(f'Ресурс {link} загружен.')
        file_name = os.path.join(element['link'].netloc, element['link'].path)
        file_name = file_name.split('.')
        ext = file_name[-1]
        file_name = '.'.join(file_name[:-1])
        file_name = f'{link_to_filename(file_name)}.{ext}'
        file_name = join(directory, file_name)
        save_file(os.path.join(directory, file_name), res, element['mode'])
        if element['obj'].get('href'):
            element['obj']['href'] = file_name
        else:
            element['obj']['src'] = file_name
        logger.info(f'Ресурс {file_name} сохранен.')


def download(url, directory):  # noqa: WPS210, C901, WPS213
    """
    Загрузка и сохранение сайта.

    :param url: Адрес сайта.
    :param directory: Директория для сохранения сайта.
    :return: Полный путь к сохраненному сайту.
    """
    # Проверка директории
    directory = return_path(directory)

    # Будущее имя файла
    file_name = link_to_filename(url)

    # Проверка и получение html-страницы
    page_name = f'{file_name}.html'
    page_name = join(directory, page_name)
    text_html = load_file(url)

    # Сохранение страницы.
    save_file(page_name, text_html)

    # Создание папки для ресурсов
    res_dir = join(directory, f'{file_name}_files')
    mk_dir(res_dir)

    # Поиск всех ресурсов для скачивания.
    # Струтура list_res:
    # list = [
    #   словарь1,
    #   словарь2,
    #   ....
    # ]
    # Структура словаря:
    # dict = {
    #   'link': urlparse('параметр href/src ресурса'),
    #   'obj': ссылка на искомый элемент soup,
    # }
    soup = BeautifulSoup(text_html, 'html.parser')
    list_res = find_resource(soup)
    logger.debug(f'Изначальный список{list_res}')

    # Удаление "неправильных" ресурсов
    netloc = urlparse(url).netloc
    scheme = urlparse(url).scheme
    path = urlparse(url).path
    for index, item in enumerate(list_res):
        logger.debug(f'Проверяется ресурс {list_res[index]["obj"]}')
        if item['link'].netloc != netloc and item['link'].netloc != '':
            logger.debug('Удален!!! Другой домен.')
            list_res[index] = None  # удаление ссылок на другие домены
        elif '.' not in basename(item['link'].path):
            logger.debug('Удален!!! Не файл.')
            list_res[index] = None  # удаление ссылок ссылающися не на файлы
    logger.debug(f'Список после удаление {list_res}')

    list_res = [res for res in list_res if res]
    # создание ссылок на скачивание у каждого ресурса
    for item in list_res:
        item['link'].scheme = scheme
        item['link'].netloc = netloc
        if isabs(item['link'].path):
            item['link'].path = f"{path}{item['link'].path}"
    logger.debug(f'Список после реобразования ссылок {list_res}')

    # Сохранение ресурсов и изменение ссылки на него
    save_resources(list_res, res_dir)

    # Сохранение изменного html
    text_html = soup.prettify()
    save_file(page_name, text_html)

    return abspath(page_name)

# def download(page, dir_path):  # noqa: WPS210, C901, WPS213
#     """
#     Загрузка и сохранение сайта.
#
#     :param page: Адрес сайта.
#     :param dir_path: Директория для сохранения сайта.
#     :return: Полный путь к сохраненному сайту.
#     """
#     if not dir_path:
#         dir_path = getcwd()
#     elif not exists(dir_path):
#         logger.error(f'Директории {dir_path} не существует.')
#         raise FileNotFoundError(f'Директории {dir_path} не существует.')
#     logging.info('Проверка наличия папки пройдена.')
#
#     if 'http' not in page:
#         logger.error('Неполный адрес сайта.')
#         raise ValueError('Неполный адрес сайта.')
#     logging.info('Проверка адреса сайта пройдена.')
#
#     try:
#         resp = requests.get(page)
#     except requests.RequestException:
#         raise ConnectionError('Ошибка подключения.')
#     if resp.status_code != requests.codes.ok:
#         logger.error('Сайт не доступен.')
#         raise ConnectionError('Сайт не доступен.')
#     logging.info('Проверка доступности сайта пройдена.')
#
#     file_name = link_to_filename(page)
#
#     # Сохранение страницы.
#     page_name = f'{file_name}.html'
#     page_name = join(dir_path, page_name)
#     text_html = resp.text
#     try:
#         with open(page_name, 'w') as html_file:
#             html_file.write(text_html)
#     except OSError:
#         logger.error('Не удалось сохранить сайт.')
#         raise OSError('Не удалось сохранить сайт.')
#     logging.info('Страница сайта сохранена.')
#
#     # Поиск и сохранение ресурсов.
#     src_dir = f'{file_name}_files'
#     if not exists(src_dir):
#         try:
#             mkdir(src_dir)
#         except OSError:
#             logger.error('Не удалось создать папку для ресурсов.')
#             raise OSError('Не удалось создать папку для ресурсов.')
#     attr = [
#         ('img', 'src'),
#         ('link', 'href'),
#         ('script', 'src'),
#     ]
#     for tag_arg in attr:
#         logging.info(f'Сохранение {tag_arg}.')
#         text_html = download_and_replace(tag_arg, src_dir, text_html, page)
#
#     try:
#         with open(page_name, 'w') as html_file:  # noqa: WPS440
#             html_file.write(text_html)
#     except OSError:
#         logger.error('Не удалось сохранить изменение ссылок на ресурсы.')
#         raise OSError('Не удалось сохранить изменение ссылок на ресурсы.')
#     logging.info('Ссылки на ресурсы страницы изменены.')
#
#     return abspath(page_name)
# def download_and_replace(attr, path, text_html, page):  # noqa: WPS210
#     """
#     Загрузка ресурсов.
#
#     Загрузка ресурсов этой страницы и сохранение их в директории path.
#     Возвращает измененный text_html.
#
#     :param page: адрес страницы
#     :param attr: кортеж с тегом и параметром
#     :param path: директория для сохранения
#     :param text_html: html-страница
#     :return: изменненная страница
#     """
#     soup = BeautifulSoup(text_html, 'html.parser')
#
#     count = len(soup.find_all(attr[0]))
#     progress_bar = Bar(f'Обработка тега {attr[0]}: ', max=count)
#
#     for tag in soup.find_all(attr[0]):
#         # Проверка ссылки
#         link = tag.get(attr[1])
#         if link is None:
#             continue
#         if '.' not in link.split('/')[-1]:
#             continue
#         if 'http' in link and (urlparse(page).netloc !=urlparse(link).netloc):
#             continue
#
#         ext = link.split('.')[-1]
#         if 'http' in link:
#             file_name = f'{urlparse(page).netloc}{urlparse(page).path}'
#         elif link[0] == '/':
#             file_name = f'{urlparse(page).netloc}{link}'
#         else:
#             file_name = f'{urlparse(page).netloc}{urlparse(page).path}/{link}'
#
#         # получения ресурса
#         try:
#             rsc = requests.get(f'{urlparse(page).scheme}://{file_name}')
#         except requests.RequestException:
#             logger.error(f'Ресурс {file_name} не доступен.')
#             continue
#         if rsc.status_code != requests.codes.ok:
#             logger.error(
#                 f"""Сайт вернул, код ошибки {rsc.status_code}.
#                 Ресурс {file_name} не доступен.""",  # noqa: WPS318
#             )
#             continue
#         file_name = link_to_filename(
#             file_name[0:file_name.rfind(ext) - 1],  # noqa: WPS349
#         )
#         logging.info(f'Ресурс {file_name} получен.')
#
#         file_name = f'{file_name}.{ext}'
#         file_name = join(path, file_name)
#
#         # сохранение файла с ресурсом
#         try:
#             with open(file_name, 'wb') as img:
#                 img.write(rsc.content)
#         except OSError:
#             logging.info(f'Не удалось сохранить файл {file_name}.')
#         else:
#             logging.info(f'Ресурс {file_name} сохранен.')
#
#         # изменение ссылки на ресурс
#         tag[attr[1]] = file_name
#
#         progress_bar.next()  # noqa: B305
#
#     progress_bar.finish()
#
#     return soup.prettify()
