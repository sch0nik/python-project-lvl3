"""
Главный модуль утилиты.

Сохраняет только ('img', 'src'), ('link', 'href'), ('script', 'src').
Для вклчения логирования нужно добавить переменную окржения:
PAGE_LOADER_LOG=уровень_логирования ('debug', 'info', 'warning', 'error').
"""
import logging
from os import getcwd
from os.path import abspath, join, exists

from page_loader.fs import mk_dir, save_file
from page_loader.html_processing import (
    url_to_filename,
    get,
    page_processing,
    save_resources,
)

log = logging.getLogger('page_loader')


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
    log.info('Проверка наличия папки пройдена.')

    page_name = url_to_filename(url)
    page_name = join(directory, page_name)
    res_dir = f'{page_name[:-5]}_files'

    text_html = get(url).text

    log.debug('Получение списка ресурсов')
    list_res, text_html = page_processing(url, text_html, res_dir)

    log.debug('Сохранение html-файла')
    if not save_file(page_name, text_html):
        raise OSError(f'Не удалось сохранить файл {page_name}')

    log.debug('Сохранение списка ресурсов')
    if list_res:
        mk_dir(res_dir)
        save_resources(list_res, directory)

    return abspath(page_name)
