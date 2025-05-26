# stac-api

Central stac api instance

## Create Virtual Environment

```bash
make venv
```

## Install Dependencies

```bash
make install
```

## Run Tests

```bash
make test
```

## Run Linter

```bash
make lint
```

## Local development

For local development, the repo has a docker compose file that spins up the services

```bash
docker-compose up -d --build
```

### Build Image locally

```bash
make docker-build
```

### Spin up the server locally

```bash
make run
```

## Running Migration

Migration can be run with `Pypgstac` CLI.

```bash
pypgstac migrate
```
