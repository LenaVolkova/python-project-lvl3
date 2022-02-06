import os
import requests
from bs4 import BeautifulSoup
import logging
from page_loader.error import FileError
from page_loader.parse_and_name import find_resourcetags, make_name
from page_loader.request_and_save import download_and_save_resources, make_request, save_to_file


LOG = logging.getLogger(__name__)


def download(url, output_path):
    if output_path is None:
        output_path = os.getcwd()
    if not os.path.isdir(output_path):
        LOG.error("wrong output path: {} is not a directory".format(output_path))
        raise FileError('wrong path', output_path)
    if not os.access(output_path, os.W_OK):
        LOG.error("No permissions for writing to output path {}".format(output_path))
        raise FileError("no permissions for writing", output_path)
    LOG.info('{} will be save to {}'.format(url, output_path))
    main_request = make_request(url)
    soup = BeautifulSoup(main_request.text, 'html.parser')
    resources_for_download = find_resourcetags(soup, url)
    name = make_name(url)[0]
    resource_dirname = "{}_files".format(name)
    main_dir_path = os.path.join(output_path, "{}_files".format(name))
    download_and_save_resources(resources_for_download, main_dir_path, resource_dirname)
    filepath = os.path.join(output_path, "{}.html".format(name))
    save_to_file(filepath, "w+", soup.prettify())
    return filepath
