from contextlib import asynccontextmanager

from fastapi import FastAPI

from work_orchestration.api.health import router as health_router
from work_orchestration.api.works import router as works_router
from work_orchestration.config.container import get_event_publisher, shutdown_messaging
from work_orchestration.config.settings import app_configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_event_publisher()
    yield
    shutdown_messaging()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
app.include_router(works_router)
