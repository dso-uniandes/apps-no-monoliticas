import logging
import threading

import pulsar
from pulsar import ConsumerType
from pulsar.schema import AvroSchema

from published_language.v1.partner_rules_evaluated import PartnerRulesEvaluatedV1
from work_orchestration.aplicacion.comandos.create_work import CreateWork
from work_orchestration.aplicacion.handlers.create_work import CreateWorkHandler


logger = logging.getLogger(__name__)


class PartnerRulesEvaluatedConsumer:
    def __init__(
        self,
        pulsar_url: str,
        topic: str,
        subscription: str,
        create_work_handler: CreateWorkHandler,
        listener_name: str | None = None,
    ):
        self._pulsar_url = pulsar_url
        self._topic = topic
        self._subscription = subscription
        self._handler = create_work_handler
        self._listener_name = listener_name
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._client: pulsar.Client | None = None
        self._consumer = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name='partner-rules-evaluated-consumer',
            daemon=True,
        )
        self._thread.start()
        logger.info(
            'Consumidor PartnerRulesEvaluatedV1 iniciado topic=%s subscription=%s',
            self._topic,
            self._subscription,
        )

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._close_resources()

    def _run(self) -> None:
        try:
            client_kwargs = {}
            if self._listener_name:
                client_kwargs['listener_name'] = self._listener_name
            self._client = pulsar.Client(self._pulsar_url, **client_kwargs)
            self._consumer = self._client.subscribe(
                self._topic,
                self._subscription,
                consumer_type=ConsumerType.Shared,
                schema=AvroSchema(PartnerRulesEvaluatedV1),
            )

            while not self._stop_event.is_set():
                try:
                    msg = self._consumer.receive(timeout_millis=1000)
                except Exception:
                    continue

                try:
                    evento: PartnerRulesEvaluatedV1 = msg.value()
                    logger.info(
                        'PartnerRulesEvaluatedV1 received: %s',
                        evento.external_reference,
                    )
                    if evento.allowed:
                        comando = CreateWork(
                            partner_id=evento.partner_id,
                            external_reference=evento.external_reference,
                            city=evento.city,
                            country=evento.country,
                        )
                        self._handler.handle(comando)
                    self._consumer.acknowledge(msg)
                except Exception:
                    logger.exception('Error procesando PartnerRulesEvaluatedV1')
                    try:
                        self._consumer.negative_acknowledge(msg)
                    except Exception:
                        logger.exception('No se pudo hacer negative_acknowledge')
        except Exception:
            logger.exception('Fallo el loop del consumidor PartnerRulesEvaluatedV1')
        finally:
            self._close_resources()

    def _close_resources(self) -> None:
        if self._consumer is not None:
            try:
                self._consumer.close()
            except Exception:
                logger.exception('Error cerrando consumer Pulsar')
            self._consumer = None

        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                logger.exception('Error cerrando client Pulsar')
            self._client = None
