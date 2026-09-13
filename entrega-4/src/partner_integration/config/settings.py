from pydantic_settings import BaseSettings
from typing import Any, Literal


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'partner-integration'
    MESSAGING_ENABLED: bool = False
    PULSAR_URL: str = 'pulsar://localhost:6650'
    PULSAR_LISTENER_NAME: str = ''
    EVALUATE_PARTNER_RULES_TOPIC: str = (
        'persistent://public/default/hda-evaluate-partner-rules-v1'
    )
    PERSISTENCE_BACKEND: Literal['inmemory', 'sqlite'] = 'inmemory'
    DATABASE_URL: str = 'sqlite:////data/partner_integration.db'
    AUTO_CREATE_SCHEMA: bool = True


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Partner Integration',
    'version': settings.APP_VERSION,
}
