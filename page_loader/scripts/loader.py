"""Точка входа."""
import logging
import os

from page_loader import download, log_level
from page_loader.cli import parse_args


def main():  # noqa: D103
    level = log_level.get(os.environ.get('PAGE_LOADER_LOG'))
    file_name = os.environ.get('PAGE_LOADER_LOG_DESTINATION')
    if level:
        if file_name:
            logging.basicConfig(
                level=level,
                format='%(asctime)s %(levelname)s %(module)s %(message)s',
                filename='page_loader.log',
                filemode='w',
            )
        else:
            logging.basicConfig(
                level=level,
                format='%(asctime)s %(levelname)s %(module)s %(message)s',
            )

    args = parse_args()
    print(download(args.page, args.output))


if __name__ == '__main__':
    main()
