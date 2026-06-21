# Makefile for ambient-expense-agent

.PHONY: install playground lint test generate-traces grade

install:
	uv sync --system-certs --link-mode copy

playground:
	uv run python expense_agent/fast_api_app.py

lint:
	agents-cli lint

test:
	uv run pytest tests/unit tests/integration

run:
	uv run python expense_agent/fast_api_app.py

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	uv run python tests/eval/grade_override.py
