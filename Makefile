.PHONY: setup run test lint fmt clean

setup:
	python -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt

run:
	.venv/bin/python -m ics_analysis $(ARGS)

test:
	.venv/bin/python -m pytest tests/ -v --cov=ics_analysis --cov-report=term-missing

lint:
	.venv/bin/ruff check ics_analysis/ tests/

fmt:
	.venv/bin/ruff format ics_analysis/ tests/

clean:
	rm -rf .venv __pycache__ ics_analysis/__pycache__ .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
