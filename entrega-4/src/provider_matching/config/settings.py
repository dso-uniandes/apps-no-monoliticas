from pydantic_settings import BaseSettings
from typing import Any, Literal


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'provider-matching'
    PULSAR_URL: str = 'pulsar://localhost:6650'
    PULSAR_LISTENER_NAME: str = ''
    MESSAGING_ENABLED: bool = False
    WORK_CREATED_TOPIC: str = 'persistent://public/default/hda-work-created-v1'
    WORK_CREATED_SUBSCRIPTION: str = 'hda-provider-matching-v1'
    PERSISTENCE_BACKEND: Literal['inmemory', 'sqlite'] = 'inmemory'
    DATABASE_URL: str = 'sqlite:////data/provider_matching.db'
    AUTO_CREATE_SCHEMA: bool = True


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Provider Matching',
    'version': settings.APP_VERSION,
}
