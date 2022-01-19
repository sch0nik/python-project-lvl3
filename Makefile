build:
	rm -rf dist
	poetry build

package-install:
	pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader tests

test:
	poetry run pytest -vv page_loader tests

install:
	poetry install

coverage:
	poetry run coverage run -m pytest
	poetry run coverage xml
	poetry run coverage html

.PHONY: install lint build package-install test coverage
