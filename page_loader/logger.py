"""Настройка логгера."""
import logging


def setup_logger():
    """ Настройка логера. """
    fmt_line = (
        '%(asctime)s::%(levelname)s::%(module)s::%(funcName)s::%(message)s'
    )
    logging.basicConfig(
        level=logging.ERROR,
        format=fmt_line,
    )
