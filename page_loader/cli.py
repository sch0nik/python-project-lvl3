"""Инициалиация и парсинг командно строки."""
import argparse


def parse_args():
    """
    Создание парсера параметров.

    :return: возвращает созданный парсер.
    """
    parser = argparse.ArgumentParser(description='Загрузчик страниц.')
    parser.add_argument('page')
    parser.add_argument(
        '-o',
        '--output',
        default='',
        help='Директория для сохранения файлов',
    )

    return parser.parse_args()
