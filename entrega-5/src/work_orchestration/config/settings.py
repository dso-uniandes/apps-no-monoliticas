from pydantic_settings import BaseSettings
from typing import Any, Literal


class Settings(BaseSettings):
    APP_VERSION: str = '1'
    SERVICE_NAME: str = 'work-orchestration'
    PULSAR_URL: str = 'pulsar://localhost:6650'
    PULSAR_LISTENER_NAME: str = ''
    MESSAGING_ENABLED: bool = False
    WORK_CREATED_TOPIC: str = 'persistent://public/default/hda-work-created-v1'
    WORK_CANCELLED_TOPIC: str = 'persistent://public/default/hda-work-cancelled-v1'
    PARTNER_RULES_EVALUATED_TOPIC: str = (
        'persistent://public/default/hda-partner-rules-evaluated-v1'
    )
    PARTNER_RULES_EVALUATED_SUBSCRIPTION: str = 'hda-work-orchestration-v1'
    MATCHING_COMPLETED_TOPIC: str = 'persistent://public/default/hda-matching-completed-v1'
    MATCHING_COMPLETED_SUBSCRIPTION: str = 'hda-work-orchestration-saga-log-v1'
    MATCHING_FAILED_TOPIC: str = 'persistent://public/default/hda-matching-failed-v1'
    MATCHING_FAILED_SUBSCRIPTION: str = 'hda-work-orchestration-compensation-v1'
    SAGA_LOG_DATABASE_URL: str = 'sqlite:////data/saga_log.db'
    PERSISTENCE_BACKEND: Literal['inmemory', 'postgres'] = 'inmemory'
    DATABASE_URL: str = 'postgresql+psycopg://hda:hda@localhost:5432/hda'
    AUTO_CREATE_SCHEMA: bool = True


settings = Settings()

app_configs: dict[str, Any] = {
    'title': 'Work Orchestration',
    'version': settings.APP_VERSION,
}
