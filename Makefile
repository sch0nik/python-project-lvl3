build:
	poetry build

package-install:
	pip install --user dist/*.whl

linter:
	poetry run flake8 page_loader
