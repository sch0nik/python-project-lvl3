"""Работа с файловой системой."""
import logging
from os import getcwd, mkdir
from os.path import exists

log = logging.getLogger('page_loader')


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
        log.error(f'Директории {directory} не существует.')
        raise FileNotFoundError(f'Директории {directory} не существует.')
    log.info('Проверка наличия папки пройдена.')
    return directory


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
        log.error(f'Не удалось сохранить файл {file_name}. Ошибка {exc}')
        return False
    log.info(f'Файл {file_name} сохранен.')
    return True


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
            log.error('Не удалось создать папку для ресурсов.')
            raise OSError('Не удалось создать папку для ресурсов.')
