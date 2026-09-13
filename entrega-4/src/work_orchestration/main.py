import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from work_orchestration.api.health import router as health_router
from work_orchestration.api.works import router as works_router
from work_orchestration.config.container import (
    get_work_repository,
    shutdown_messaging,
    shutdown_persistence,
    start_messaging,
)
from work_orchestration.config.settings import app_configs

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_work_repository()
    start_messaging()
    yield
    shutdown_messaging()
    shutdown_persistence()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
app.include_router(works_router)
