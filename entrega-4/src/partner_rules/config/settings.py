from pydantic_settings import BaseSettings
from typing import Any


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'partner-rules'
    MESSAGING_ENABLED: bool = False
    PULSAR_URL: str = 'pulsar://localhost:6650'
    PULSAR_LISTENER_NAME: str = ''
    EVALUATE_PARTNER_RULES_TOPIC: str = (
        'persistent://public/default/hda-evaluate-partner-rules-v1'
    )
    EVALUATE_PARTNER_RULES_SUBSCRIPTION: str = 'hda-partner-rules-v1'
    PARTNER_RULES_EVALUATED_TOPIC: str = (
        'persistent://public/default/hda-partner-rules-evaluated-v1'
    )


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Partner Rules',
    'version': settings.APP_VERSION,
}
