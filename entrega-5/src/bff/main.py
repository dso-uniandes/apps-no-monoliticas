import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from bff.api.health import router as health_router
from bff.api.partner_requests import router as partner_requests_router
from bff.config.settings import app_configs
from bff.infraestructura.http_clients import close_client, get_client

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_client()
    yield
    await close_client()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
app.include_router(partner_requests_router)
