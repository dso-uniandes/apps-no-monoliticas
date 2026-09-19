import logging

import pulsar
from pulsar.schema import AvroSchema

from provider_matching.aplicacion.puertos.event_publisher import EventPublisher
from published_language.v1.matching_completed import MatchingCompletedV1
from published_language.v1.matching_failed import MatchingFailedV1


logger = logging.getLogger(__name__)


class PulsarEventPublisher(EventPublisher):
    def __init__(
        self,
        pulsar_url: str,
        completed_topic: str,
        failed_topic: str,
        listener_name: str | None = None,
    ):
        client_kwargs = {}
        if listener_name:
            client_kwargs['listener_name'] = listener_name
        self._client = pulsar.Client(pulsar_url, **client_kwargs)
        self._completed_producer = self._client.create_producer(
            completed_topic,
            schema=AvroSchema(MatchingCompletedV1),
        )
        self._failed_producer = self._client.create_producer(
            failed_topic,
            schema=AvroSchema(MatchingFailedV1),
        )

    def publish(self, evento: object) -> None:
        if isinstance(evento, MatchingCompletedV1):
            self._completed_producer.send(evento, partition_key=evento.work_id or '')
            logger.info('MatchingCompletedV1 published: %s', evento.work_id)
            return

        if isinstance(evento, MatchingFailedV1):
            self._failed_producer.send(evento, partition_key=evento.work_id or '')
            logger.info('MatchingFailedV1 published: %s', evento.work_id)
            return

        raise TypeError(f'Evento de matching no soportado: {type(evento).__name__}')

    def close(self) -> None:
        try:
            self._completed_producer.close()
            self._failed_producer.close()
        finally:
            self._client.close()
