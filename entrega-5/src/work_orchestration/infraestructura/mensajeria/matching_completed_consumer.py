import logging
import threading

import pulsar
from pulsar import ConsumerType
from pulsar.schema import AvroSchema

from published_language.v1.matching_completed import MatchingCompletedV1
from work_orchestration.infraestructura.saga_log import SagaLog


logger = logging.getLogger(__name__)


class MatchingCompletedConsumer:
    def __init__(
        self,
        pulsar_url: str,
        topic: str,
        subscription: str,
        saga_log: SagaLog,
        listener_name: str | None = None,
    ):
        self._pulsar_url = pulsar_url
        self._topic = topic
        self._subscription = subscription
        self._saga_log = saga_log
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
            name='matching-completed-consumer',
            daemon=True,
        )
        self._thread.start()
        logger.info(
            'Consumidor MatchingCompletedV1 iniciado topic=%s subscription=%s',
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
                schema=AvroSchema(MatchingCompletedV1),
            )

            while not self._stop_event.is_set():
                try:
                    msg = self._consumer.receive(timeout_millis=1000)
                except Exception:
                    continue

                try:
                    evento: MatchingCompletedV1 = msg.value()
                    logger.info('MatchingCompletedV1 received: %s', evento.work_id)
                    self._saga_log.add_step(
                        evento.external_reference,
                        'MATCHING_COMPLETED',
                        'DONE',
                        f'provider_id={evento.provider_id}',
                    )
                    self._consumer.acknowledge(msg)
                except Exception:
                    logger.exception('Error procesando MatchingCompletedV1')
                    try:
                        self._consumer.negative_acknowledge(msg)
                    except Exception:
                        logger.exception('No se pudo hacer negative_acknowledge')
        except Exception:
            logger.exception('Fallo el loop del consumidor MatchingCompletedV1')
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
