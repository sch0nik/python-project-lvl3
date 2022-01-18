build:
	poetry build

package-install:
	pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader

test:
	poetry run pytest -vv

install:
	poetry install

.PHONY: install lint build package-install
