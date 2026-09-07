import logging
import threading

import pulsar
from pulsar import ConsumerType
from pulsar.schema import AvroSchema

from published_language.v1.work_created import WorkCreatedV1
from provider_matching.aplicacion.comandos.process_matching import ProcessMatching
from provider_matching.aplicacion.handlers.process_matching import ProcessMatchingHandler


logger = logging.getLogger(__name__)


class WorkCreatedConsumer:
    def __init__(
        self,
        pulsar_url: str,
        topic: str,
        subscription: str,
        process_matching_handler: ProcessMatchingHandler,
    ):
        self._pulsar_url = pulsar_url
        self._topic = topic
        self._subscription = subscription
        self._handler = process_matching_handler
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
            name='work-created-consumer',
            daemon=True,
        )
        self._thread.start()
        logger.info(
            'Consumidor WorkCreatedV1 iniciado topic=%s subscription=%s type=Shared',
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
            self._client = pulsar.Client(self._pulsar_url, listener_name='internal')
            self._consumer = self._client.subscribe(
                self._topic,
                self._subscription,
                consumer_type=ConsumerType.Shared,
                schema=AvroSchema(WorkCreatedV1),
            )

            while not self._stop_event.is_set():
                try:
                    msg = self._consumer.receive(timeout_millis=1000)
                except Exception:
                    continue

                try:
                    evento: WorkCreatedV1 = msg.value()
                    logger.info('WorkCreatedV1 received: %s', evento.work_id)
                    comando = ProcessMatching(work_id=evento.work_id)
                    matching = self._handler.handle(comando)
                    logger.info('Matching processed: %s', matching.id)
                    self._consumer.acknowledge(msg)
                except Exception:
                    logger.exception('Error procesando WorkCreatedV1')
                    try:
                        self._consumer.negative_acknowledge(msg)
                    except Exception:
                        logger.exception('No se pudo hacer negative_acknowledge')
        except Exception:
            logger.exception('Fallo el loop del consumidor WorkCreatedV1')
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
