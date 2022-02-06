"""Настройка логгера."""
import logging


def logger(log_name, level_log=logging.ERROR):
    """
    Настройка логера.

    :param log_name:
    :param level_log: уровень логирования
    :return: None
    """
    log = logging.getLogger('page_loader')
    fmt_line = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(message)s',
    )

    err_handler = logging.StreamHandler()
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(fmt_line)
    log.addHandler(err_handler)

    file_handler = logging.FileHandler('page_loader.log', mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fmt_line)
    log.addHandler(file_handler)

    log.setLevel(level_log)

    return log