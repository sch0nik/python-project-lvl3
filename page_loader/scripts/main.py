from page_loader import download
from page_loader.cli import parse_args


def main():
    args = parse_args()
    print(download(args.page, args.output))


if __name__ == 'main':
    main()
