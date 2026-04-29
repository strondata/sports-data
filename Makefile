.PHONY: install test lint typecheck run

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy src

run:
	poetry run sports-data run
