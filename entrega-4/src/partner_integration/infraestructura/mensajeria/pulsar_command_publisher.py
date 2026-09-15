import logging

import pulsar
from pulsar.schema import AvroSchema

from published_language.v1.evaluate_partner_rules import EvaluatePartnerRulesV1
from partner_integration.aplicacion.puertos.command_publisher import CommandPublisher


logger = logging.getLogger(__name__)


class PulsarCommandPublisher(CommandPublisher):
    def __init__(self, pulsar_url: str, topic: str, listener_name: str | None = None):
        client_kwargs = {}
        if listener_name:
            client_kwargs['listener_name'] = listener_name
        self._client = pulsar.Client(pulsar_url, **client_kwargs)
        self._producer = self._client.create_producer(
            topic,
            schema=AvroSchema(EvaluatePartnerRulesV1),
        )

    def publish(self, comando: object) -> None:
        if not isinstance(comando, EvaluatePartnerRulesV1):
            raise TypeError(
                'PulsarCommandPublisher solo publica EvaluatePartnerRulesV1, '
                f'recibido: {type(comando).__name__}'
            )

        self._producer.send(
            comando,
            partition_key=comando.external_reference or '',
        )
        logger.info(
            'EvaluatePartnerRulesV1 published: %s',
            comando.external_reference,
        )

    def close(self) -> None:
        try:
            self._producer.close()
        finally:
            self._client.close()
