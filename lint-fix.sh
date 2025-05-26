#!/usr/bin/env bash

set -o verbose

# poetry run mypy . --exclude tests/
poetry run black .
poetry run ruff check --fix
