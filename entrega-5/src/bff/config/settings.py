from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'bff'
    PARTNER_INTEGRATION_URL: str = 'http://localhost:8001'
    PARTNER_RULES_URL: str = 'http://localhost:8002'
    WORK_ORCHESTRATION_URL: str = 'http://localhost:8003'
    PROVIDER_MATCHING_URL: str = 'http://localhost:8004'
    HTTP_TIMEOUT_SECONDS: float = 5.0


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Hogar de los Alpes BFF',
    'version': settings.APP_VERSION,
    'description': (
        'Backend For Frontend de la POC. Unica puerta de entrada publica: recibe la '
        'solicitud del partner y expone el estado consolidado de la SAGA '
        '(Work + Saga Log) bajo un solo recurso.'
    ),
}
