"""
Главный модуль утилиты.

Сохраняет только ('img', 'src'), ('link', 'href'), ('script', 'src').
Для вклчения логирования нужно добавить переменную окржения:
PAGE_LOADER_LOG=уровень_логирования ('debug', 'info', 'warning', 'error').
"""
import logging
import string
import sys
from os import getcwd, mkdir
from os.path import abspath, basename, exists, join
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
    """Замена ParseResult."""

    def __init__(self, res):  # noqa: D107
        self.scheme = res.scheme
        self.netloc = res.netloc
        self.path = res.path
        self.params = res.params  # noqa: WPS110
        self.query = res.query
        self.fragment = res.fragment

    def __get__(self, instance, owner):  # noqa: D105
        return (
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        )

    def __repr__(self):  # noqa: D105
        return f'{self.scheme}_{self.netloc}_{self.path}'


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
    """
    Загрузка файла.

    :param url: ссылка на файл
    :param mode: режим w - текстовый файл, wb - бинарный
    :param missing:  если False, то вызывается исключение
    :return: либо содержимое файла, либо None
    """
    if 'http' not in url:
        logger.error('Неполный адрес.')
        raise ValueError('Неполный адрес.')
    logging.info('Проверка адреса пройдена.')

    try:  # noqa: WPS503
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


def save_file(file_name, conteined, mode='w'):
    """
    Безопасное сохранение файла.

    :param file_name: путь и имя файла
    :param conteined: содержимое файла
    :param mode: режим, соответственно функии open
    :return: ничего
    """
    try:
        with open(file_name, mode) as res_file:
            res_file.write(conteined)
    except OSError as exc:
        logger.error(f'Не удалось сохранить файл {file_name}. Ошибка {exc}')
        raise OSError(f'Не удалось сохранить файл {file_name}. Ошибка {exc}')
    logging.info(f'Файл {file_name} сохранен.')


def mk_dir(res_dir):
    """
    безопасное содание директории.

    :param res_dir: путь и название директории
    :return: None
    """
    if not exists(res_dir):
        try:
            mkdir(res_dir)
        except OSError:
            logger.error('Не удалось создать папку для ресурсов.')
            raise OSError('Не удалось создать папку для ресурсов.')


def find_resource(soup):
    """
    Нахожение ресурсов в soup.

    :param soup: объект BeautifulSoup
    :return: список ресурсов
    """
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


def save_resources(list_res, directory):  # noqa: WPS210
    """
    Сохранение списка ресурсов.

    :param list_res: спсиок ресурссов
    :param directory: директория для сохранения
    :return: None
    """
    logger.debug(f'Сохранение ресурсов. Всего {len(list_res)}')
    progress_bar = Bar('Сохранение: ', max=len(list_res))
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
        # Образование имени файла
        file_name = element['link'].netloc
        file_name += '' if element['link'].path[0] == '/' else '/'
        file_name += element['link'].path
        if '.' in file_name.split('/')[-1]:
            file_name = file_name.split('.')
            ext = file_name[-1]
            file_name = '.'.join(file_name[:-1])
        else:
            ext = 'html'

        file_name = f'{link_to_filename(file_name)}.{ext}'

        file_name = join(directory, file_name)
        save_file(file_name, res, element['mode'])
        if element['obj'].get('href'):
            element['obj']['href'] = file_name
        else:
            element['obj']['src'] = file_name
        logger.info(f'Ресурс {file_name} сохранен.')
        progress_bar.next()  # noqa: B305

    progress_bar.finish()


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
    # [
    #   словарь1,
    #   словарь2,
    #   ....
    # ]
    # Структура словаря:
    # {
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
    for index, elem in enumerate(list_res):
        logger.debug(f'Проверяется ресурс {list_res[index]["obj"]}')
        if elem['link'].netloc != netloc and elem['link'].netloc != '':
            logger.debug('Удален!!! Другой домен.')
            list_res[index] = None  # удаление ссылок на другие домены
        # elif '.' not in basename(elem['link'].path):
        #     logger.debug('Удален!!! Не файл.')
        #     list_res[index] = None  # удаление ссылок ссылающися не на файлы
    logger.debug(f'Список после удаление {list_res}')

    list_res = [res for res in list_res if res]
    # создание ссылок на скачивание у каждого ресурса
    for elem in list_res:
        elem['link'].scheme = scheme
        elem['link'].netloc = netloc
        # if elem['link'].path[0] == '/':
        #     elem['link'].path = f"{path}{elem['link'].path}"
        # else:
        #     elem['link'].path = f"{elem['link'].path}"

    logger.debug(f'Список после реобразования ссылок {list_res}')

    # Сохранение ресурсов и изменение ссылки на него
    save_resources(list_res, res_dir)

    # Сохранение изменного html
    text_html = soup.prettify()
    save_file(page_name, text_html)

    return abspath(page_name)
