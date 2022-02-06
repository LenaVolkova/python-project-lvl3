import logging
import os
from progress.bar import Bar
from page_loader.error import FileError
from page_loader.parse_and_name import make_extension
import requests


LOG = logging.getLogger(__name__)


def download_and_save_resources(resources, dirpath, dirurl):
    if not os.path.isdir(dirpath):
        try:
            os.mkdir(dirpath)
        except OSError as e:
            LOG.error(e)
            raise FileError("can't make directory for resources", dirpath)
    bar = Bar('Downloading resources', max=len(resources))
    for resource in resources:
        resource_request = make_request(resource["url"], False)
        if resource_request:
            tag = resource["tag"]
            attribute = resource["attr"]
            if resource["ext"] == '':
                if 'content-type' in resource_request.headers:
                    content_t = resource_request.headers['content-type']
                else:
                    content_t = ''
                resource["ext"] = make_extension(content_t, tag)
            resname = resource["filename"] + resource["ext"]
            respath = os.path.join(dirpath, resname)
            save_to_file(respath, 'wb+', resource_request.content, False)
            resource["res"][attribute] = os.path.join(dirurl, resname)
        bar.next()
    bar.finish()
    return


def make_request(url, raise_Exception=True):
    try:
        response = requests.get(url)
    except requests.RequestException as e:
        LOG.error("Network error while processing the url {}: {}".format(url, e))
        response = False
        if raise_Exception:
            raise e
    try:
        response.raise_for_status()
    except requests.RequestException as e:
        LOG.error("Error while requesting the page {}: {}".format(url, e))
        response = False
        if raise_Exception:
            raise e
    return response


def save_to_file(filepath, mode, content, raise_Exception=True):
    try:
        with open(filepath, mode) as f:
            f.write(content)
    except OSError as e:
        LOG.error(e)
        if raise_Exception:
            raise FileError("can't save", filepath)
