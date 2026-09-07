from pydantic_settings import BaseSettings
from typing import Any


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'work-orchestration'
    PULSAR_URL: str = 'pulsar://localhost:6650'
    MESSAGING_ENABLED: bool = False
    WORK_CREATED_TOPIC: str = 'persistent://public/default/hda-work-created-v1'


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Work Orchestration',
    'version': settings.APP_VERSION,
}
