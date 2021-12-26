install:
	poetry install

build:
	rm -rf dist
	poetry build

package-install:
	python3 -m pip install --user dist/*.whl

package-install-reinforced:
	python3 -m pip install --user --force-reinstall dist/*.whl

page_loader:
	poety run page_loader -h

lint:
	poetry run flake8 page_loader

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=./page_loader --cov-report xml

.PHONY: page_loader