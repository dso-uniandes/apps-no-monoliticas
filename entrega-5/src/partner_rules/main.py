import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from partner_rules.api.health import router as health_router
from partner_rules.config.container import (
    get_partner_rule_repository,
    start_messaging,
    shutdown_messaging,
    shutdown_persistence,
)
from partner_rules.config.settings import app_configs

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_partner_rule_repository()
    start_messaging()
    yield
    shutdown_messaging()
    shutdown_persistence()


app = FastAPI(lifespan=lifespan, **app_configs)
app.include_router(health_router)
