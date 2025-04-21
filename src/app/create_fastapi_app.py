from contextlib import asynccontextmanager
from typing import Any

import anyio
from arq.connections import RedisSettings, create_pool
from fastapi import Depends, FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import JSONResponse
from redis.asyncio import ConnectionPool, Redis

from app.api.dependencies.user import get_current_superuser
from app.core import db_helper

# from app.core.utils import queue, rate_limit, cache,redis_client
# from arq import create_pool
# from arq.connections import RedisSettings
from app.core.config import EnvironmentOption, settings
from app.core.logger import logging
from app.core.utils import redis_client, task_queue
from app.models import Base

logger = logging.getLogger(__name__)


# -------------- database --------------
async def create_tables() -> None:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# -------------- redis --------------
async def create_redis_pool() -> None:
    try:
        redis_client.pool = ConnectionPool.from_url(settings.redis_client.REDIS_URL)
        redis_client.client = Redis(connection_pool=redis_client.pool)  # type: ignore
        await redis_client.client.ping()
        logger.info("Redis client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection pool: {e}")
        raise


async def close_redis_pool() -> None:
    await redis_client.client.aclose()  # type: ignore


# -------------- queue --------------
async def create_redis_queue_pool() -> None:
    task_queue.pool = await create_pool(
        RedisSettings(
            host=settings.redis_client.REDIS_HOST,
            port=settings.redis_client.REDIS_PORT,
        )
    )


async def close_redis_queue_pool() -> None:
    await task_queue.pool.aclose()  # type: ignore


# -------------- cache --------------
# async def create_redis_cache_pool() -> None:
#     cache.pool = ConnectionPool.from_url(settings.redis_cache.REDIS_CACHE_URL)
#     cache.client = Redis(connection_pool=cache.pool)  # type: ignore


# async def close_redis_cache_pool() -> None:
#     await cache.client.aclose()  # type: ignore
#
#
#
#
# # -------------- rate limit --------------
# async def create_redis_rate_limit_pool() -> None:
#     rate_limit.pool = ConnectionPool.from_url(
#         settings.redis_rate_limiter.REDIS_RATE_LIMIT_URL
#     )
#     rate_limit.client = Redis.from_pool(rate_limit.pool)  # type: ignore
#
#
# async def close_redis_rate_limit_pool() -> None:
#     await rate_limit.client.aclose()  # type: ignore


# -------------- application --------------
async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = number_of_tokens


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await set_threadpool_tokens()

    if settings.db.CREATE_TABLES_ON_START:
        await create_tables()
    if settings.db.DROP_TABLES_ON_START:
        await drop_tables()
    await create_redis_pool()
    await create_redis_queue_pool()
    yield
    # shutdown
    await close_redis_pool()

    await close_redis_queue_pool()

    await db_helper.dispose()


def register_static_docs_routes(app: FastAPI):
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html(
        current_user: Any = Depends(
            get_current_superuser if settings.environment.ENVIRONMENT == EnvironmentOption.STAGING else lambda: None
        ),
    ):
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html(
        current_user: Any = Depends(
            get_current_superuser if settings.environment.ENVIRONMENT == EnvironmentOption.STAGING else lambda: None
        ),
    ):
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
        )


# -------------- application --------------
def create_app() -> FastAPI:
    logger.info("Starting application setup...")
    cond = settings.environment.ENVIRONMENT == EnvironmentOption.PRODUCTION.value
    logger.info(f"Current environment: {settings.environment.ENVIRONMENT} cond: {cond}")
    app = FastAPI(
        default_response_class=JSONResponse,
        lifespan=lifespan,
        docs_url=None if cond else "/docs",
        redoc_url=None if cond else "/redoc",
        openapi_url=None if cond else "/openapi.json",
    )
    if not cond:
        logger.info("Registering static docs routes...")
        register_static_docs_routes(app)
        app.docs_url = "/docs"
        app.redoc_url = "/redoc"

    logger.info("Setting app metadata...")
    app.title = settings.app_settings.APP_NAME
    app.description = settings.app_settings.APP_DESCRIPTION
    app.contact = {
        "name": settings.app_settings.CONTACT_NAME,
        "email": settings.app_settings.CONTACT_EMAIL,
    }
    app.license_info = {"name": settings.app_settings.LICENSE_NAME}
    logger.info("Application setup completed successfully")
    return app
