.PHONY: install dev test lint type run

install:
	pip install -e .[dev]

dev:
	uvicorn ai_agent_system.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check src tests

type:
	mypy src

run:
	uvicorn ai_agent_system.main:app --host 0.0.0.0 --port 8000
