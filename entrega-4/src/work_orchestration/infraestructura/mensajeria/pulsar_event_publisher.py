import logging

import pulsar
from pulsar.schema import AvroSchema

from published_language.v1.work_created import WorkCreatedV1
from work_orchestration.aplicacion.puertos.event_publisher import EventPublisher


logger = logging.getLogger(__name__)


class PulsarEventPublisher(EventPublisher):
    def __init__(self, pulsar_url: str, topic: str, listener_name: str | None = None):
        self._pulsar_url = pulsar_url
        self._topic = topic
        client_kwargs = {}
        if listener_name:
            client_kwargs['listener_name'] = listener_name
        self._client = pulsar.Client(pulsar_url, **client_kwargs)
        self._producer = self._client.create_producer(
            topic,
            schema=AvroSchema(WorkCreatedV1),
        )

    def publish(self, evento: object) -> None:
        if not isinstance(evento, WorkCreatedV1):
            raise TypeError(
                f'PulsarEventPublisher solo publica WorkCreatedV1, recibido: {type(evento).__name__}'
            )

        self._producer.send(
            evento,
            partition_key=evento.work_id or '',
        )
        logger.info('WorkCreatedV1 published: %s', evento.work_id)

    def close(self) -> None:
        try:
            self._producer.close()
        finally:
            self._client.close()
