"""
Утилита командной строки для скачивания сайтов.

Скачивает либо в текущую директорию,либо в указанную
через параметр -о или --output.
"""

import logging

from page_loader.download import download

log_level = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
}
