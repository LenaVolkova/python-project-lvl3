from page_loader import download
import requests_mock
import tempfile
import os


url = 'https://ru.hexlet.io/courses'
url_img = 'https://ru.hexlet.io/assets/professions/nodejs.png'
url_link1 = '/assets/application.css'
url_link2 = '/courses'
url_script = 'https://ru.hexlet.io/packs/js/runtime.js'

with open("./tests/fixtures/input.html", 'r') as input_file:
    input_text = input_file.read()
with open("./tests/fixtures/input_res.html", 'r') as input_res_file:
    input_res_text = input_res_file.read()
with open("./tests/fixtures/output.html", 'r') as output_file:
    output_text = output_file.read()
with open("./tests/fixtures/picture.png", 'rb') as img_file:
    img_content = img_file.read()
with open("./tests/fixtures/ru-hexlet-io-courses.html", 'r') as output_file:
    output_text1 = output_file.read()


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


def test_downloading_page_with_images():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with requests_mock.Mocker() as m:
            m.get(url, text=input_text)
            m.get(url_img, content=img_content, headers={'content-type': 'png'})
            filename = download(url, tmpdirname)
            assert filename == tmpdirname + '/ru-hexlet-io-courses.html'
            with open(filename, 'r') as file1:
                output = file1.read()
            assert output == output_text
            dir_name = os.path.join(tmpdirname, 'ru-hexlet-io-courses_files')
            assert os.path.exists(dir_name)
            img_filename = os.path.join(dir_name, 'ru-hexlet-io-assets-professions-nodejs.png')
            assert os.path.exists(img_filename)
            assert os.path.isfile(img_filename)


def test_downloading_page_and_resources():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with requests_mock.Mocker() as m:
            m.get(url, text=input_res_text)
            m.get(url_img, content=img_content, headers={'content-type': 'image/png'})
            m.get(url_link1, text="assets and application css", headers={'content-type': 'text/css; charset=utf8'})
            m.get(url_link2, text=input_res_text, headers={'content-type': 'text/html; charset=utf8'})
            m.get(url_script, text="local script", headers={'content-type': 'text/javascript; charset=utf8'})
            filename = download(url, tmpdirname)
            assert filename == tmpdirname + '/ru-hexlet-io-courses.html'
            with open(filename, 'r') as file1:
                output = file1.read()
            assert output == output_text1
            dir_name = os.path.join(tmpdirname, 'ru-hexlet-io-courses_files')
            assert os.path.exists(dir_name)
            img_filename = os.path.join(dir_name, 'ru-hexlet-io-assets-professions-nodejs.png')
            assert os.path.exists(img_filename)
            assert os.path.isfile(img_filename)
            css_filename = os.path.join(dir_name, 'ru-hexlet-io-assets-application.css')
            assert os.path.exists(css_filename)
            assert os.path.isfile(css_filename)
            html_filename = os.path.join(dir_name, 'ru-hexlet-io-courses.html')
            assert os.path.exists(html_filename)
            assert os.path.isfile(html_filename)
            js_filename = os.path.join(dir_name, 'ru-hexlet-io-packs-js-runtime.js')
            assert os.path.exists(js_filename)
            assert os.path.isfile(js_filename)


def test_status_404():
    text1 = 'testdata\n'
    with tempfile.TemporaryDirectory() as tmpdirname:
        with requests_mock.Mocker() as m:
            m.get(url, text=text1, status_code=404)
            try:
                download(url, tmpdirname)
            except Exception:
                assert True
