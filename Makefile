SHELL := /usr/bin/env bash

.PHONY: venv install test lint run

help:
	@echo "venv - create virtual environment using pyenv"
	@echo "install - install packages with poetry"
	@echo "test - run unit tests"
	@echo "check - run linter and checks"
	@echo "fix - fix linter and checks"
	@echo "run - spins up uvicorn server at 0.0.0.0 and port 8000"


venv:
	pyenv virtualenv 3.11 stac-api && pyenv local stac-api

install:
	poetry install

test:
	poetry run pytest -vv tests --cov=app --cov-report term-missing

check:
	./lint-check.sh

fix:
	./lint-fix.sh

run:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app --no-access-log
