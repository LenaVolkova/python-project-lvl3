#!/usr/bin/env python3


import argparse
import os
from posixpath import dirname
import requests
import re
from bs4 import BeautifulSoup


def download(url, output_path):
    if output_path is None:
        output_path = os.getcwd()
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    dirname = make_name(url, output_path, "dir")
    for img in soup.find_all('img'):
        image = img.get('src')
        if to_download(url, image):
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
            image_url = make_imgurl(url, image)
            print(image_url)
            new_r = requests.get(image_url)
            imgname = make_img_name(image_url, dirname)
            print(imgname)
            with open(imgname, "wb+") as img_file:
                img_file.write(new_r.content)    
            img['src'] = imgname
              
    filename = make_name(url, output_path, "file")
    with open(filename, "w+") as f:
        f.write(soup.prettify())
    return filename


def get_schema(url):
    if '://' in url:
        return ''.join([url.split('://')[0], '://'])
    return ''


def get_domain(url):
    if '://' in url:
        url = url.split('://')[1]
    if ':' in url:
        return url.split(':')[0]
    return url.split('/')[0]
    

def make_name(url, output_path, key):
    if len(url.split("://", maxsplit=1)) == 2:
        url_name = url.split("://", maxsplit=1)[1]
    else:
        url_name = url
    urlname = re.sub(r'[^\w]', '-', url_name)
    if key == "file":
        name = '.'.join([urlname, 'html'])
    if key == "dir":
        name = '_'.join([urlname, 'files'])
    return os.path.join(output_path, name)


def make_img_name(url, output_path):
    if '://' in url:
        url_name = url.split("://")[1]
    else:
        url_name = url
    if '.' not in url_name:
        img_name = re.sub(r'[^\w]', '-', url_name)
    else:
        after_last_fullstop = url_name.split(".")[-1]
        if len(after_last_fullstop) <= 4 and after_last_fullstop.isalpha():
            name = re.sub(r'[^\w]', '-', '.'.join(re.split(r'\.',url_name)[0:-1]))
            img_name = '.'.join([name, after_last_fullstop])
        else:
            img_name = re.sub(r'[^\w]', '-', url_name)
    return os.path.join(output_path, img_name)



def make_imgurl (url, image):
    url_schema = get_schema(url)
    url_domain = get_domain(url)
    if image[0] == "/":
        return ''.join([url_schema, url_domain, image])
    if "://" in image:
        return image
    return ''.join([url, image])


def to_download(url, img_url):
    if img_url[0] == "/":
        return True
    if get_domain(url) == get_domain(img_url):
        return True
    return False

    

def main():
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url', metavar='url', type=str, nargs=1,
                        help='url for loading')
    parser.add_argument('-o', '--output', help='output dir (default: /app)')
    args = parser.parse_args()
    file_path = download(args.url[0], args.output)
    print(file_path)


if __name__ == '__main__':
    main()
