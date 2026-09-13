import logging

import pulsar
from pulsar.schema import AvroSchema

from published_language.v1.evaluate_partner_rules import EvaluatePartnerRulesV1
from partner_integration.aplicacion.puertos.event_publisher import EventPublisher


logger = logging.getLogger(__name__)


class PulsarEventPublisher(EventPublisher):
    def __init__(self, pulsar_url: str, topic: str, listener_name: str | None = None):
        client_kwargs = {}
        if listener_name:
            client_kwargs['listener_name'] = listener_name
        self._client = pulsar.Client(pulsar_url, **client_kwargs)
        self._producer = self._client.create_producer(
            topic,
            schema=AvroSchema(EvaluatePartnerRulesV1),
        )

    def publish(self, evento: object) -> None:
        if not isinstance(evento, EvaluatePartnerRulesV1):
            raise TypeError(
                'PulsarEventPublisher solo publica EvaluatePartnerRulesV1, '
                f'recibido: {type(evento).__name__}'
            )

        self._producer.send(
            evento,
            partition_key=evento.external_reference or '',
        )
        logger.info(
            'EvaluatePartnerRulesV1 published: %s',
            evento.external_reference,
        )

    def close(self) -> None:
        try:
            self._producer.close()
        finally:
            self._client.close()
