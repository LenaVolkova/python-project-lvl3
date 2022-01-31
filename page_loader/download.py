import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from progress.bar import Bar
import logging


TAGS = {"img": "src", "link": "href", "script": "src"}
LOG = logging.getLogger(__name__)
TEMPLATE = r'[^\w]'
SYMB = '-'


class DownloadingErrors(Exception):
    pass


class RequestError(DownloadingErrors):
    def __init__(self, url, code):
        self.url = url
        self.code = code
        super().__init__(
            f"RequestError: {url}, status_code = {code}"
        )


class NetworkError(DownloadingErrors):
    def __init__(self, url):
        self.url = url
        super().__init__(
            f"NetworkError: {url} can't be downloaded"
        )


class FileError(DownloadingErrors):
    def __init__(self, info, path):
        self.path = path
        self.info = info
        super().__init__(
            f"FileError: {info} {path}"
        )


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
    name = make_filename(url)[0]
    dirurl = "{}_files".format(name)
    dirname = os.path.join(output_path, "{}_files".format(name))
    filename = os.path.join(output_path, "{}.html".format(name))
    r = make_request(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    resources_for_download = find_tags(soup, url)
    download_and_save_resources(resources_for_download, dirname, dirurl)
    save_to_file(filename, "w+", soup.prettify())
    return filename


def find_tags(soup, url):
    list_of_resources = []
    for tag in TAGS:
        for res in soup.find_all(tag):
            attribute = TAGS[tag]
            resource = res.get(attribute)
            if not to_download(url, resource):
                continue
            resource_url = urljoin(url, resource)
            filename, ext = make_filename(resource_url)
            res_for_downloading = {
                "res": res,
                "tag": tag,
                "attr": attribute,
                "url": resource_url,
                "filename": filename,
                "ext": ext
            }
            list_of_resources.append(res_for_downloading)
    return list_of_resources


def download_and_save_resources(list_of_resources, dirname, dirurl):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    bar = Bar('Downloading resources', max=len(list_of_resources))
    for resource in list_of_resources:
        new_r = make_request(resource["url"], False)
        if new_r:
            tag = resource["tag"]
            attribute = resource["attr"]
            if resource["ext"] == '':
                if 'content-type' in new_r.headers:
                    content_t = new_r.headers['content-type']
                else:
                    content_t = ''
                resource["ext"] = make_extension(content_t, tag)
            resname = "{}.{}".format(resource["filename"], resource["ext"])
            respath = os.path.join(dirname, resname)
            save_to_file(respath, 'wb+', new_r.content, False)
            resource["res"][attribute] = os.path.join(dirurl, resname)
        bar.next()
    bar.finish()
    return


def make_filename(url):
    extension = ''
    res_url = urlparse(url)
    url_name = res_url.netloc + res_url.path
    if '.' not in url_name:
        res_name = make_name_by_template(url_name)
    else:
        after_last_fullstop = url_name.split(".")[-1]
        if len(after_last_fullstop) <= 4 and after_last_fullstop.isalpha():
            part_of_name = '.'.join(url_name.split(".")[0:-1])
            res_name = make_name_by_template(part_of_name)
            extension = after_last_fullstop
        else:
            res_name = make_name_by_template(url_name)
    return res_name, extension


def make_name_by_template(name, template=TEMPLATE, replacement=SYMB):
    return re.sub(template, replacement, name)


def make_extension(content_type, tag):
    extensions = {
        'gif': 'gif',
        'jpeg': 'jpeg',
        'png': 'png',
        'tiff': 'tiff',
        'css': 'css',
        'csv': 'csv',
        'html': 'html',
        'javascript': 'js',
        'xml': 'xml'}
    for k in extensions:
        if k in content_type:
            return extensions[k]
    if tag == 'link':
        return 'html'
    if tag == 'script':
        return 'js'
    return ''


def to_download(url, res_url):
    return urlparse(url).netloc == urlparse(res_url).netloc or urlparse(res_url).netloc == ''


def make_request(url, raise_Exception=True):
    try:
        response = requests.get(url)
    except Exception as e:
        LOG.error("Network error while processing the url {}: {}".format(url, e))
        response = False
        if raise_Exception:
            raise NetworkError(url) from e
    try:
        response.raise_for_status()
    except Exception as e:
        LOG.error("Error while requesting the page {}: {}".format(url, e))
        status_code = response.status_code
        response = False
        if raise_Exception:
            raise RequestError(url, status_code) from e
    return response


def save_to_file(filename, mode, content, raise_Exception=True):
    try:
        with open(filename, mode) as f:
            f.write(content)
    except Exception as e:
        LOG.error(e)
        if raise_Exception:
            raise FileError("can't save", filename)
