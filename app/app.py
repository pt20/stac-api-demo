import logging.config

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from app.logging import configure_logging, AccessLogMiddleware
from stac_fastapi.api.app import StacApi
from stac_fastapi.api.models import create_get_request_model, create_post_request_model
from stac_fastapi.extensions.core import (
    FieldsExtension,
    FilterExtension,
    QueryExtension,
    SortExtension,
    TokenPaginationExtension,
    TransactionExtension,
)
from stac_fastapi.extensions.core.filter.filter import FilterConformanceClasses
from stac_fastapi.pgstac.core import CoreCrudClient
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from stac_fastapi.pgstac.transactions import TransactionsClient
from stac_fastapi.pgstac.types.search import PgstacSearch

from app.config import config, config_postgres_settings
from app.error import CustomExceptionMiddleware

meta_router = APIRouter(tags=["Meta"])


@meta_router.get(path="/boom", name="meta:boom")
async def get_boom() -> dict:
    _ = 1 / 0
    return {"ok": False}


def create_api() -> StacApi:
    extensions = [
        # STAC API Extensions
        QueryExtension(),
        SortExtension(),
        FieldsExtension(),
        FilterExtension(
            conformance_classes=[
                FilterConformanceClasses.FILTER,
                FilterConformanceClasses.BASIC_CQL2,
                FilterConformanceClasses.CQL2_JSON,
                FilterConformanceClasses.CQL2_TEXT,
                FilterConformanceClasses.ITEMS,
            ],
        ),
        # stac_fastapi extensions
        TokenPaginationExtension(),
        TransactionExtension(
            client=TransactionsClient(),
            settings=config,
            response_class=ORJSONResponse,
        ),
    ]
    post_request_model = create_post_request_model(extensions, base_model=PgstacSearch)

    return StacApi(
        client=CoreCrudClient(),
        extensions=extensions,
        response_class=ORJSONResponse,
        search_get_request_model=create_get_request_model(extensions),
        search_post_request_model=post_request_model,
        settings=config,
    )


def create_app(api: StacApi) -> FastAPI:

    app: FastAPI = api.app

    @app.on_event("startup")
    async def startup_event() -> None:
        await connect_to_db(app, postgres_settings=config_postgres_settings)

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        await close_db_connection(app)

    logging.config.dictConfig(configure_logging(config.ENV))

    # order of middleware matters - keep CustomExceptionMiddleware on top - bitte
    app.add_middleware(CustomExceptionMiddleware)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    app.include_router(meta_router)

    return app
