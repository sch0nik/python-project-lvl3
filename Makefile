build:
	rm -rf dist
	poetry build

package-install:
	pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader

test:
	poetry run pytest -vv page_loader tests

install:
	poetry install

coverage:
	poetry run coverage run -m pytest
	poetry run coverage xml
	poetry run coverage html

start:
	rm -rf site/*
	poetry run python3 -m page_loader.scripts.loader -o site 'https://pypi.org/project/progress'

start_log:
	rm -rf site/*
	export PAGE_LOADER_LOG='info' &&\
	poetry run python3 -m page_loader.scripts.loader -o site 'https://www.google.com'
	unset PAGE_LOADER_LOG

start_err:
	rm -rf site/*
	export PAGE_LOADER_LOG='info' &&\
	poetry run python3 -m page_loader.scripts.loader -o site 'https://www.sdgsagd.com'
	unset PAGE_LOADER_LOG

.PHONY: install lint build package-install test coverage
