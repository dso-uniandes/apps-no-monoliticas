from pydantic_settings import BaseSettings
from typing import Any


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'partner-rules'
    MESSAGING_ENABLED: bool = False


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Partner Rules',
    'version': settings.APP_VERSION,
}
