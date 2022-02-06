from page_loader import download
import requests
import tempfile
import os
import pytest


url = 'https://ru.hexlet.io/courses'
url_img = 'https://ru.hexlet.io/assets/professions/nodejs.png'
url_link1 = '/assets/application.css'
url_link2 = '/courses'
url_script = 'https://ru.hexlet.io/packs/js/runtime.js'
url_for_exception1 = 'ht://www.yandex.ru'
url_for_exception1 = 'https://asapcg.com/1'

image_filename = './tests/fixtures/picture.png'
input_filename = './tests/fixtures/input.html'
input_res_filename = './tests/fixtures/input_res.html'
output_filename = './tests/fixtures/output.html'
output_filename1 = './tests/fixtures/ru-hexlet-io-courses.html'
output_filename2 = './tests/fixtures/ru-hexlet-io-courses_res.html'
input_without_attribute = './tests/fixtures/input_tst.html'


def test_download(requests_mock):
    tmpdirname = tempfile.TemporaryDirectory()
    requests_mock.get(url, text='testdata\n')
    res_text = requests.get(url).text
    filename = download(url, tmpdirname.name)
    assert filename == tmpdirname.name + '/ru-hexlet-io-courses.html'
    with open(filename, 'r') as f:
        content = f.read()
        assert content == res_text


def test_downloading_page_with_images(requests_mock):
    with open(input_filename, 'r') as input_file:
        input_text = input_file.read()
    with open(image_filename, 'rb') as img_file:
        img_content = img_file.read()
    with open(output_filename, 'r') as output_file:
        output_text = output_file.read()
    tmpdirname = tempfile.TemporaryDirectory()
    requests_mock.get(url, text=input_text)
    requests_mock.get(url_img, content=img_content, headers={'content-type': 'png'})
    filename = download(url, tmpdirname.name)
    assert filename == tmpdirname.name + '/ru-hexlet-io-courses.html'
    with open(filename, 'r') as file1:
        output = file1.read()
    assert output == output_text
    dir_name = os.path.join(tmpdirname.name, 'ru-hexlet-io-courses_files')
    assert os.path.exists(dir_name)
    img_filename = os.path.join(dir_name, 'ru-hexlet-io-assets-professions-nodejs.png')
    assert os.path.exists(img_filename)
    assert os.path.isfile(img_filename)
    with open(img_filename, 'rb') as img_file_res:
        img_res = img_file_res.read()
    assert img_res == img_content


def test_attribute_missing(requests_mock):
    tmpdirname = tempfile.TemporaryDirectory()
    with open(input_without_attribute, 'r') as input_without_attribute_file:
        input_no_attr = input_without_attribute_file.read()
    requests_mock.get(url, text=input_no_attr)
    filename = download(url, tmpdirname.name)
    assert filename == tmpdirname.name + '/ru-hexlet-io-courses.html'


def test_downloading_page_and_resources(requests_mock):
    tmpdirname = tempfile.TemporaryDirectory()
    with open(image_filename, 'rb') as img_file:
        img_content = img_file.read()
    with open(input_res_filename, 'r') as input_res_file:
        input_res_text = input_res_file.read()
    with open(output_filename1, 'r') as output_file1:
        output_text1 = output_file1.read()
    with open(output_filename2, 'r') as output_file2:
        output_text2 = output_file2.read()
    requests_mock.get(url, text=input_res_text)
    requests_mock.get(url_img, content=img_content, headers={'content-type': 'image/png'})
    requests_mock.get(url_link1, text="assets and application css", headers={'content-type': 'text/css; charset=utf8'})
    requests_mock.get(url_link2, text=input_res_text, headers={'content-type': 'text/html; charset=utf8'})
    requests_mock.get(url_script, text="local script", headers={'content-type': 'text/javascript; charset=utf8'})
    filename = download(url, tmpdirname.name)
    assert filename == tmpdirname.name + '/ru-hexlet-io-courses.html'
    with open(filename, 'r') as file1:
        output = file1.read()
    assert output == output_text1
    dir_name = os.path.join(tmpdirname.name, 'ru-hexlet-io-courses_files')
    assert os.path.exists(dir_name)
    img_filename = os.path.join(dir_name, 'ru-hexlet-io-assets-professions-nodejs.png')
    assert os.path.exists(img_filename)
    assert os.path.isfile(img_filename)
    with open(img_filename, 'rb') as img_file_res:
        img_res = img_file_res.read()
    assert img_res == img_content
    css_filename = os.path.join(dir_name, 'ru-hexlet-io-assets-application.css')
    assert os.path.exists(css_filename)
    assert os.path.isfile(css_filename)
    with open(css_filename, 'r') as css_file_res:
        css_res = css_file_res.read()
    assert css_res == 'assets and application css'
    html_filename = os.path.join(dir_name, 'ru-hexlet-io-courses.html')
    assert os.path.exists(html_filename)
    assert os.path.isfile(html_filename)
    with open(html_filename, 'r') as html_file_res:
        html_res = html_file_res.read()
    assert html_res == output_text2
    js_filename = os.path.join(dir_name, 'ru-hexlet-io-packs-js-runtime.js')
    assert os.path.exists(js_filename)
    assert os.path.isfile(js_filename)
    with open(js_filename, 'r') as js_file_res:
        js_res = js_file_res.read()
    assert js_res == 'local script'


def test_status_404(requests_mock):
    text1 = 'testdata\n'
    tmpdirname = tempfile.TemporaryDirectory()
    requests_mock.get(url, text=text1, status_code=404)
    with pytest.raises(Exception, match=r".*404.*"):
        download(url, tmpdirname.name)


@pytest.mark.xfail(raises=requests.RequestException)
def test_exception():
    tmpdirname = tempfile.TemporaryDirectory()
    download("ht://asapcg.com", tmpdirname.name)
    