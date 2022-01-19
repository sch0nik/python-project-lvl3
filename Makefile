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

.PHONY: install lint build package-install test
