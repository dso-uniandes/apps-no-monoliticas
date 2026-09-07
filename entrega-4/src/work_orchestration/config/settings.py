from pydantic_settings import BaseSettings
from typing import Any


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'work-orchestration'


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Work Orchestration',
    'version': settings.APP_VERSION,
}
