import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from partner_integration.api.health import router as health_router
from partner_integration.api.partner_requests import router as partner_requests_router
from partner_integration.config.container import (
    get_event_publisher,
    get_partner_request_repository,
    shutdown_messaging,
    shutdown_persistence,
)
from partner_integration.config.settings import app_configs

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_partner_request_repository()
    get_event_publisher()
    yield
    shutdown_messaging()
    shutdown_persistence()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
app.include_router(partner_requests_router)
