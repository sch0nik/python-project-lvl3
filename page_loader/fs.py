"""Работа с файловой системой."""
import logging
from os import mkdir
from os.path import exists

log = logging.getLogger('page_loader')


def save_file(file_name, conteined, mode='w'):
    """
    Безопасное сохранение файла.

    :param file_name: путь и имя файла
    :param conteined: содержимое файла
    :param mode: режим, соответственно функии open
    :return: ничего
    """
    log.debug(f'Сохранение {file_name}')
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
