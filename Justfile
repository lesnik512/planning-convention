default: install lint test

install:
    uv sync --all-extras --all-groups

lint:
    uv run eof-fixer .
    uv run ruff format .
    uv run ruff check . --fix
    uv run ty check

test *args:
    uv run pytest {{ args }}

index:
    uv run python index.py

check-planning:
    uv run python index.py --check
