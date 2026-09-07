from pydantic_settings import BaseSettings
from typing import Any


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'provider-matching'
    PULSAR_URL: str = 'pulsar://localhost:6650'
    MESSAGING_ENABLED: bool = False
    WORK_CREATED_TOPIC: str = 'persistent://public/default/hda-work-created-v1'
    WORK_CREATED_SUBSCRIPTION: str = 'hda-provider-matching-v1'


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Provider Matching',
    'version': settings.APP_VERSION,
}
