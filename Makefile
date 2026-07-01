test:
	uv run pytest

fmt:
	uv run ruff format python_actuator && uv run ruff check --fix python_actuator

wps:
	uv run flake8 python_actuator

mypy:
	uv run mypy python_actuator

ty:
	uv run ty check python_actuator

cov:
	uv run pytest --cov=python_actuator --cov-report=term-missing --cov-fail-under=85

types: ty mypy


check: fmt types wps
