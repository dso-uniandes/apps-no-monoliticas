from fastapi import FastAPI

from provider_matching.api.health import router as health_router
from provider_matching.config.settings import app_configs

app = FastAPI(**app_configs)
app.include_router(health_router)
