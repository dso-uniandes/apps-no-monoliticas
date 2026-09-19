import logging
import threading
from datetime import datetime
from uuid import UUID
from uuid import uuid4

import pulsar
from pulsar import ConsumerType
from pulsar.schema import AvroSchema

from published_language.v1.matching_failed import MatchingFailedV1
from published_language.v1.work_cancelled import WorkCancelledV1
from work_orchestration.aplicacion.puertos.event_publisher import EventPublisher
from work_orchestration.dominio.repositorios import WorkRepository
from work_orchestration.infraestructura.saga_log import SagaLog


logger = logging.getLogger(__name__)


class MatchingFailedConsumer:
    def __init__(
        self,
        pulsar_url: str,
        topic: str,
        subscription: str,
        work_repository: WorkRepository,
        event_publisher: EventPublisher,
        saga_log: SagaLog,
        listener_name: str | None = None,
    ):
        self._pulsar_url = pulsar_url
        self._topic = topic
        self._subscription = subscription
        self._repository = work_repository
        self._event_publisher = event_publisher
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
            name='matching-failed-consumer',
            daemon=True,
        )
        self._thread.start()
        logger.info(
            'Consumidor MatchingFailedV1 iniciado topic=%s subscription=%s',
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
                schema=AvroSchema(MatchingFailedV1),
            )

            while not self._stop_event.is_set():
                try:
                    msg = self._consumer.receive(timeout_millis=1000)
                except Exception:
                    continue

                try:
                    evento: MatchingFailedV1 = msg.value()
                    logger.info('MatchingFailedV1 received: %s', evento.work_id)
                    self._compensate(evento)
                    self._consumer.acknowledge(msg)
                except Exception:
                    logger.exception('Error procesando MatchingFailedV1')
                    try:
                        self._consumer.negative_acknowledge(msg)
                    except Exception:
                        logger.exception('No se pudo hacer negative_acknowledge')
        except Exception:
            logger.exception('Fallo el loop del consumidor MatchingFailedV1')
        finally:
            self._close_resources()

    def _compensate(self, evento: MatchingFailedV1) -> None:
        self._saga_log.add_step(
            evento.external_reference,
            'MATCHING_FAILED',
            'FAILED',
            evento.reason,
        )

        work = self._repository.obtener_por_id(UUID(evento.work_id))
        if work is None:
            self._saga_log.add_step(
                evento.external_reference,
                'WORK_COMPENSATION',
                'SKIPPED',
                f'Work {evento.work_id} no existe',
            )
            return

        work.cancel(evento.reason)
        self._repository.actualizar(work)
        cancelled = WorkCancelledV1(
            event_id=str(uuid4()),
            occurred_at=int(datetime.utcnow().timestamp() * 1000),
            schema_version='1',
            work_id=str(work.id),
            external_reference=evento.external_reference,
            reason=evento.reason,
            status=work.status.valor,
        )
        self._event_publisher.publish(cancelled)
        self._saga_log.add_step(
            evento.external_reference,
            'WORK_CANCELLED',
            'COMPENSATED',
            evento.reason,
        )
        logger.info('WorkCancelledV1 published: %s', work.id)

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
