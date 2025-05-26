import os
from urllib.parse import quote

from pydantic import Field
from stac_fastapi.pgstac.config import PostgresSettings, Settings


class Config(Settings):
    ENV: str = Field(default="development")

    # stac_fastapi changes these, but we want the FastAPI defaults
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"

    # stac_fastapi
    postgres_user: str = Field(default="root")
    postgres_pass: str = Field(default=quote(os.environ.get("PGPASSWORD", "test")))
    postgres_host_reader: str = Field(default="localhost")
    postgres_host_writer: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_dbname: str = Field(default="stac")


class ConfigPostgresSettings(PostgresSettings):
    """Postgres settings for the application."""

    postgres_user: str = Field(default="root")
    postgres_pass: str = Field(default=quote(os.environ.get("PGPASSWORD", "test")))
    postgres_host_reader: str = Field(default="localhost")
    postgres_host_writer: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_dbname: str = Field(default="stac")


config = Config()
config_postgres_settings = ConfigPostgresSettings(
    postgres_user=config.postgres_user,
    postgres_pass=config.postgres_pass,
    postgres_host_reader=config.postgres_host_reader,
    postgres_host_writer=config.postgres_host_writer,
    postgres_port=config.postgres_port,
    postgres_dbname=config.postgres_dbname,
)
