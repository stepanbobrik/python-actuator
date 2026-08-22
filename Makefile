test:
	uv run pytest

fmt:
	uv run ruff format src/python_actuator tests && uv run ruff check --fix src/python_actuator

wps:
	uv run flake8 src/python_actuator

mypy:
	uv run mypy src/python_actuator

ty:
	uv run ty check src/python_actuator

cov:
	uv run pytest --cov=python_actuator --cov-report=term-missing --cov-fail-under=85

reuse:
	uv run reuse --no-multiprocessing lint

types: ty mypy

check: fmt types wps reuse
