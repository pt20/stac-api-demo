#!/usr/bin/env bash

set -o verbose
set -o errexit

poetry run mypy . --exclude tests/
poetry run black . --check
poetry run ruff check
