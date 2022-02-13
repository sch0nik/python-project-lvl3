"""Точка входа."""
import logging
from sys import exit

from page_loader import download
from page_loader.cli import parse_args
from page_loader.logger import setup_logger


def main():  # noqa: D103
    setup_logger()
    args = parse_args()
    try:
        path = download(args.page, args.output)
    except Exception as exc:
        logging.exception(f'Ошибка! {exc}')
        print(f'Ошибка! {exc}')
        exit(1)
    else:
        print(path)
        logging.info(f'Результат: {path}')
        exit(0)


if __name__ == '__main__':
    main()
