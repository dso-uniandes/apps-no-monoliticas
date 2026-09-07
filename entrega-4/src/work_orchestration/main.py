from fastapi import FastAPI

from work_orchestration.api.health import router as health_router
from work_orchestration.api.works import router as works_router
from work_orchestration.config.settings import app_configs

app = FastAPI(**app_configs)
app.include_router(health_router)
app.include_router(works_router)
