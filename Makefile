build:
	rm -rf dist
	poetry build

package-install:
	pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader

test:
	poetry run pytest page_loader tests

test_log:
	poetry run pytest -o log_cli=true\
 	--log-cli-level=debug\
 	page_loader tests

install:
	poetry install

coverage:
	poetry run coverage run -m pytest
	poetry run coverage xml
	poetry run coverage html

run:
	poetry run python3 -m page_loader.scripts.loader 'https://pypi.org/project/progress'

start:
	rm -rf site/*
	poetry run python3 -m page_loader.scripts.loader -o site 'https://pypi.org/project/progress'

clean:
	rm -rf site/*

.PHONY: install lint build package-install test coverage run start
