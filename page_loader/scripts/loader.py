"""Точка входа."""
import logging
from sys import exit

from page_loader import download
from page_loader.cli import parse_args
from page_loader.logger import setup_logger


def main():  # noqa: D103
    log = setup_logger('page_loader', logging.INFO)
    args = parse_args()
    log.debug(f'Начало. {args.page} {args.output}')
    try:
        path = download(args.page, args.output)
    except Exception as exc:
        log.exception(f'Ошибка! {exc}')
        print(f'Ошибка! {exc}')
        exit(1)
    else:
        print(path)
        log.info(f'Результат: {path}')
        exit(0)


if __name__ == '__main__':
    main()
