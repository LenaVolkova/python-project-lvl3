import os
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from progress.bar import Bar
import logging
from logging import handlers


logfile = 'file.log'
log1 = logging.getLogger("my_log1")
c_handler = logging.StreamHandler()
f_handler = handlers.RotatingFileHandler(logfile, maxBytes=(1048576 * 5), backupCount=2)
log1.setLevel(logging.DEBUG)
c_handler.setLevel(logging.ERROR)
f_handler.setLevel(logging.INFO)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
log1.addHandler(c_handler)
log1.addHandler(f_handler)


def download(url, output_path):
    filename = ''
    if output_path is None:
        output_path = os.getcwd()
    if not os.access(output_path, os.W_OK):
        log1.error("No permissions for writing to output path {}".format(output_path))
        raise Exception('no permissions for writing')
    if not os.path.isdir(output_path):
        log1.error("wrong output path: {} is not a directory".format(output_path))
        raise Exception('Specified output path is not a directory')
    log1.info('{} will be save to {}'.format(url, output_path))
    r = requests.get(url)
    if r.status_code != 200:
        log1.error('response with code {}'.format(r.status_code))
        raise Exception("Cannot procerss the url")
    else:
        log1.info('response with code {}'.format(r.status_code))
        soup = BeautifulSoup(r.text, 'html.parser')
        dirname = make_name(url, output_path, "dir")
        dirurl = make_name(url, output_path, "url")
        process_tags(soup, 'img', 'src', url, dirname, dirurl)
        process_tags(soup, 'link', 'href', url, dirname, dirurl)
        process_tags(soup, 'script', 'src', url, dirname, dirurl)
        filename = make_name(url, output_path, "file")
        try:
            with open(filename, "w+") as f:
                f.write(soup.prettify())
            log1.info('{} has been downloaded to {}'.format(url, filename))
        except Exception as e:
            log1.error(e)
    return filename


def process_tags(soup, tag, attribute, url, dirname, dirurl):
    if tag == 'img':
        mode = 'wb+'
    else:
        mode = 'w+'
    bar = Bar('Downloading {}-resources'.format(tag), max=len(soup.find_all(tag)))
    for res in soup.find_all(tag):
        resource = res.get(attribute)
        if to_download(url, resource):
            log1.info("processing {}".format(resource))
            if not os.path.isdir(dirname):
                try:
                    os.mkdir(dirname)
                    log1.info('{} directory has been created'.format(dirname))
                except Exception as e:
                    log1.error(e)
            resource_url = make_imgurl(url, resource)
            new_r = requests.get(resource_url)
            if new_r.status_code != 200:
                log1.warning('response with code {} from {}'.format(new_r.status_code, resource_url))
            else:
                log1.info('response with code {} from {}'.format(new_r.status_code, resource_url))
                resname = make_res_name(resource_url, url, new_r.headers['content-type'])
                respath = os.path.join(dirname, resname)
                try:
                    with open(respath, mode) as saved_file:
                        if tag == 'img':
                            saved_file.write(new_r.content)
                        else:
                            saved_file.write(new_r.text)
                    log1.info('{} has been saved to {}'.format(resource, respath))
                except Exception as e:
                    log1.error(e)
                res[attribute] = os.path.join(dirurl, resname)
        bar.next()
    bar.finish()
    return


def make_name(url, output_path, key):
    parsed_url = urlparse(url)
    url_name = ''.join([parsed_url[1], parsed_url[2]])
    urlname = re.sub(r'[^\w]', '-', url_name)
    if key == "file":
        name = '.'.join([urlname, 'html'])
    if key == "dir":
        name = '_'.join([urlname, 'files'])
    if key == "url":
        name = '_'.join([urlname, 'files'])
        return name
    return os.path.join(output_path, name)


def make_res_name(resource, main_url, content_type):
    res_url = urlparse(resource)
    if res_url[1] == '':
        url_name = ''.join([urlparse(main_url)[1], res_url[2]])
    else:
        url_name = ''.join([res_url[1], res_url[2]])
    if '.' not in url_name:
        res_name = re.sub(r'[^\w]', '-', url_name)
    else:
        after_last_fullstop = url_name.split(".")[-1]
        if len(after_last_fullstop) <= 4 and after_last_fullstop.isalpha():
            name = re.sub(r'[^\w]', '-', '.'.join(re.split(r'\.', url_name)[0:-1]))
            res_name = '.'.join([name, after_last_fullstop])
        else:
            res_name = re.sub(r'[^\w]', '-', url_name)
    if '.' not in res_name:
        return ''.join([res_name, make_extension(content_type)])
    return res_name


def make_extension(content_type):
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
    return ''


def make_imgurl(url, image):
    image_parsed = urlparse(image)
    url_parsed = urlparse(url)
    if image_parsed[0] == '':
        schema = url_parsed[0]
    else:
        schema = image_parsed[0]
    if image_parsed[1] == '':
        domain = url_parsed[1]
    else:
        domain = image_parsed[1]
    return ''.join([schema, '://', domain, image_parsed[2]])


def to_download(url, res_url):
    if urlparse(url)[1] == urlparse(res_url)[1] or urlparse(res_url)[1] == '':
        return True
    return False
