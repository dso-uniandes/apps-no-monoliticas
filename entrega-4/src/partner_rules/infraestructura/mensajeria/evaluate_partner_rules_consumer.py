import logging
import threading

import pulsar
from pulsar import ConsumerType
from pulsar.schema import AvroSchema

from published_language.v1.evaluate_partner_rules import EvaluatePartnerRulesV1
from partner_rules.aplicacion.comandos.evaluate_partner_rules import EvaluatePartnerRules
from partner_rules.aplicacion.handlers.evaluate_partner_rules import EvaluatePartnerRulesHandler


logger = logging.getLogger(__name__)


class EvaluatePartnerRulesConsumer:
    def __init__(
        self,
        pulsar_url: str,
        topic: str,
        subscription: str,
        evaluate_handler: EvaluatePartnerRulesHandler,
        listener_name: str | None = None,
    ):
        self._pulsar_url = pulsar_url
        self._topic = topic
        self._subscription = subscription
        self._handler = evaluate_handler
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
            name='evaluate-partner-rules-consumer',
            daemon=True,
        )
        self._thread.start()
        logger.info(
            'Consumidor EvaluatePartnerRulesV1 iniciado topic=%s subscription=%s',
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
                schema=AvroSchema(EvaluatePartnerRulesV1),
            )

            while not self._stop_event.is_set():
                try:
                    msg = self._consumer.receive(timeout_millis=1000)
                except Exception:
                    continue

                try:
                    comando_remoto: EvaluatePartnerRulesV1 = msg.value()
                    logger.info(
                        'EvaluatePartnerRulesV1 received: %s',
                        comando_remoto.external_reference,
                    )
                    comando = EvaluatePartnerRules(
                        partner_id=comando_remoto.partner_id,
                        service_type=comando_remoto.service_type or None,
                        external_reference=comando_remoto.external_reference or '',
                        city=comando_remoto.city or '',
                        country=comando_remoto.country or '',
                    )
                    self._handler.handle(comando)
                    self._consumer.acknowledge(msg)
                except Exception:
                    logger.exception('Error procesando EvaluatePartnerRulesV1')
                    try:
                        self._consumer.negative_acknowledge(msg)
                    except Exception:
                        logger.exception('No se pudo hacer negative_acknowledge')
        except Exception:
            logger.exception('Fallo el loop del consumidor EvaluatePartnerRulesV1')
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
