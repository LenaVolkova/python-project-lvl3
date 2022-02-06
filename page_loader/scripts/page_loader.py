#!/usr/bin/env python3


import argparse
from page_loader.download import download
import sys
import logging.config

LOG_FILENAME = 'file.log'
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s: \n%(message)s\n",
        },
    },
    "handlers": {
        "logfile": {
            "formatter": "simple",
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 1048576,
            "filename": LOG_FILENAME,
            "backupCount": 2,
        },
        "c_output": {
            "formatter": "simple",
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "page_loader": {
            "level": "INFO",
            "handlers": [
                "c_output",
                "logfile",
            ],
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)


def main():
    log1 = logging.getLogger(__name__)
    log1.info("Launched")
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url', type=str, help='url for loading')
    parser.add_argument('-o', '--output', help='output dir (default: /app)')
    args = parser.parse_args()

    try:
        file_path = download(args.url, args.output)
        print(file_path)
        log1.info("Page has been saved to {}".format(file_path))
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
