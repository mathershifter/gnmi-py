# -*- makefile -*-

lint:
    ruff format --diff
    ruff check

reformat:
    ruff format

types:
    uv run --dev mypy ./gnmi

setup:
  uv pip sync