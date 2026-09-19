import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from provider_matching.api.health import router as health_router
from provider_matching.config.container import (
    get_matching_repository,
    shutdown_messaging,
    shutdown_persistence,
    start_messaging,
)
from provider_matching.config.settings import app_configs

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_matching_repository()
    start_messaging()
    yield
    shutdown_messaging()
    shutdown_persistence()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
