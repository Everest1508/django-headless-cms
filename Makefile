.PHONY: install install-dev build clean test publish

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

build:
	python setup.py sdist bdist_wheel

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

test:
	python -m pytest tests/

publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*

check:
	python setup.py check

