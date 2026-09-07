from contextlib import asynccontextmanager

from fastapi import FastAPI

from provider_matching.api.health import router as health_router
from provider_matching.config.container import shutdown_messaging, start_messaging
from provider_matching.config.settings import app_configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_messaging()
    yield
    shutdown_messaging()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
