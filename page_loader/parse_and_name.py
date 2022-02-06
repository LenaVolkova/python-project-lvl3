import logging
from urllib.parse import urljoin, urlparse
import os
import re


TAGS = {"img": "src", "link": "href", "script": "src"}
LOG = logging.getLogger(__name__)


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
