from contextlib import asynccontextmanager

from fastapi import FastAPI

from partner_integration.api.health import router as health_router
from partner_integration.config.container import (
    get_partner_request_repository,
    shutdown_persistence,
)
from partner_integration.config.settings import app_configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_partner_request_repository()
    yield
    shutdown_persistence()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
