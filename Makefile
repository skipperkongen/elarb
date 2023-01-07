.PHONY: build, twine, test, install

build:
	# pip install build
	python -m build

twine:
	# pip install twine
	twine upload dist/*

venv:
	python3 -m venv venv

install_dev:
	pip install -e '.[tests]'

install:
	pip install -e .

test:
	pytest

lint:
	flake8 src 
