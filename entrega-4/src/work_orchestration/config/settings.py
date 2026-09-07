from pydantic_settings import BaseSettings
from typing import Any, Literal


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'work-orchestration'
    PULSAR_URL: str = 'pulsar://localhost:6650'
    PULSAR_LISTENER_NAME: str = ''
    MESSAGING_ENABLED: bool = False
    WORK_CREATED_TOPIC: str = 'persistent://public/default/hda-work-created-v1'
    PERSISTENCE_BACKEND: Literal['inmemory', 'postgres'] = 'inmemory'
    DATABASE_URL: str = 'postgresql+psycopg://hda:hda@localhost:5432/hda'
    AUTO_CREATE_SCHEMA: bool = True


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Work Orchestration',
    'version': settings.APP_VERSION,
}
