import pytest
from page_loader.scripts.page_loader import download
import requests
import requests_mock
import tempfile
import os


url = 'https://ru.hexlet.io/courses'
url_img = 'https://ru.hexlet.io/assets/professions/nodejs.png'

with open("./tests/fixtures/input.html", 'r') as input_file:
    input_text = input_file.read()
with open("./tests/fixtures/output.html", 'r') as output_file:
    output_text = output_file.read()
with open("./tests/fixtures/picture.png", 'rb') as img_file:
    img_content = img_file.read()

def test_download():
    text1 = 'testdata\n'
    with tempfile.TemporaryDirectory() as tmpdirname:
        with requests_mock.Mocker() as m:
            m.get(url, text=text1)
            filename = download(url, tmpdirname) 
            assert filename == tmpdirname + '/ru-hexlet-io-courses.html'
            with open(filename, 'r') as f:
                content = f.read()
                assert content == text1

def test_downloading_files():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with requests_mock.Mocker() as m:
            m.get(url, text=input_text)
            m.get(url_img, content=img_content)
            filename = download(url, tmpdirname) 
            assert filename == tmpdirname + '/ru-hexlet-io-courses.html'
            dir_name = os.path.join(tmpdirname, 'ru-hexlet-io-courses_files')
            assert os.path.exists(dir_name)
            img_filename = os.path.join(dir_name, 'ru-hexlet-io-assets-professions-nodejs.png')
            assert os.path.exists(img_filename)
            assert os.path.isfile(img_filename)
