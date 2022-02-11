"""Работа с файловой системой."""
import logging
from os import mkdir
from os.path import exists


def save_file(file_name, conteined):
    """
    Безопасное сохранение файла.

    :param file_name: путь и имя файла
    :param conteined: содержимое файла
    :return: ничего
    """
    mode = 'w' if isinstance(conteined, str) else 'wb'
    try:
        with open(file_name, mode) as res_file:
            res_file.write(conteined)
    except OSError as exc:
        logging.exception(f'Файл не сохранен {file_name}. Ошибка {exc}')
        raise OSError(f'Файл не сохранен {file_name}. Ошибка {exc}')
    except TypeError as exc:
        logging.exception(f'Файл не сохранен {file_name}. Ошибка {exc}')
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
            logging.error('Не удалось создать папку для ресурсов.')
            raise OSError('Не удалось создать папку для ресурсов.')
