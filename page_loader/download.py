import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from progress.bar import Bar
import logging


TAGS = {"img": "src", "link": "href", "script": "src"}
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


def find_resourcetags(soup, url):
    resources = []
    for tag, attribute in TAGS.items():
        for res in soup.find_all(tag):
            resource = res.get(attribute)
            LOG.info('{} is processing'.format(resource))
            if not should_download(url, resource):
                continue
            LOG.info('{} is to be saved'.format(resource))
            resource_url = urljoin(url, resource)
            filename, ext = make_name(resource_url)
            resource_for_downloading = {
                "res": res,
                "tag": tag,
                "attr": attribute,
                "url": resource_url,
                "filename": filename,
                "ext": ext
            }
            resources.append(resource_for_downloading)
    return resources


def download_and_save_resources(resources, dirpath, dirurl):
    if not os.path.isdir(dirpath):
        try:
            os.mkdir(dirpath)
        except OSError as e:
            LOG.error(e)
            raise FileError("can't make directory", dirpath)
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


def make_name(url):
    parsed_url = urlparse(url)
    name_url = parsed_url.netloc + parsed_url.path
    name, ext = os.path.splitext(name_url)
    return re.sub(r'[^\w]', '-', name), ext


def make_extension(content_type, tag):
    extensions = {
        'gif': '.gif',
        'jpeg': '.jpeg',
        'png': '.png',
        'tiff': '.tiff',
        'css': '.css',
        'csv': '.csv',
        'html': '.html',
        'javascript': '.js',
        'xml': '.xml'}
    for k in extensions:
        if k in content_type:
            return extensions[k]
    if tag == 'link':
        return '.html'
    if tag == 'script':
        return '.js'
    return ''


def should_download(url, res_url):
    return urlparse(url).netloc == urlparse(res_url).netloc or urlparse(res_url).netloc == ''


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
            raise e
