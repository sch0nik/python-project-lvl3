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
	export PAGE_LOADER_LOG='info' &&\
	poetry run python3 -m page_loader.scripts.loader -o site 'https://www.google.com'

start_log_file:
	rm -rf site/*
	export PAGE_LOADER_LOG='info' &&\
	export PAGE_LOADER_LOG_DESTINATION='page_loader.log' &&\
	poetry run python3 -m page_loader.scripts.loader -o site 'https://www.google.com'

.PHONY: install lint build package-install test coverage
