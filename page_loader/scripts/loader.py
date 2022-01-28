"""Точка входа."""
import logging
import os
from sys import exit

from page_loader import download, log_level
from page_loader.cli import parse_args


def main():  # noqa: D103
    level = log_level.get(os.environ.get('PAGE_LOADER_LOG'))
    if level:
        logging.basicConfig(
            level=level,
            format='%(asctime)s %(levelname)s %(module)s %(message)s',
        )

    args = parse_args()
    try:
        path = download(args.page, args.output)
    except FileNotFoundError as exc:
        print(exc)
        exit(1)
    except ValueError as exc:
        print(exc)
        exit(1)
    except ConnectionError as exc:
        print(exc)
        exit(1)
    except OSError as exc:
        print(exc)
        exit(1)
    except Exception as exc:
        print(f'Неизвестная ощибка! {exc}')
        exit(1)
    else:
        print(path)
        exit(0)


if __name__ == '__main__':
    main()
