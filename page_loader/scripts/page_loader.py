#!/usr/bin/env python3


import argparse
from page_loader.download import download
import sys


def main():
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url', metavar='url', type=str, nargs=1,
                        help='url for loading')
    parser.add_argument('-o', '--output', help='output dir (default: /app)')
    args = parser.parse_args()

    try:
        file_path = download(args.url[0], args.output)
        print(file_path)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
