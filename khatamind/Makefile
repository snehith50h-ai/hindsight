.PHONY: setup run test lint sim

setup:
	pip install -e ".[dev]" && pre-commit install

run:
	uvicorn apps.api.main:app --reload

test:
	pytest -q

lint:
	ruff check . && mypy core && lint-imports

sim:
	python -m simulation.run --seed 42 --days 90 --memory on
