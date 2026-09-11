from fastapi import FastAPI

from partner_rules.api.health import router as health_router
from partner_rules.config.settings import app_configs


app = FastAPI(**app_configs)
app.include_router(health_router)
