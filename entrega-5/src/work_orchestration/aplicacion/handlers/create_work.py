from seedwork.aplicacion.comandos import ComandoHandler
import logging

from work_orchestration.aplicacion.comandos.create_work import CreateWork
from work_orchestration.aplicacion.mappers.work_created_integration_mapper import (
    WorkCreatedIntegrationMapper,
)
from work_orchestration.aplicacion.puertos.event_publisher import EventPublisher
from work_orchestration.dominio.entidades import Work
from work_orchestration.dominio.eventos import WorkCreated
from work_orchestration.dominio.repositorios import WorkRepository


logger = logging.getLogger(__name__)


class CreateWorkHandler(ComandoHandler):
    def __init__(
        self,
        repositorio: WorkRepository,
        event_publisher: EventPublisher,
    ):
        self._repositorio = repositorio
        self._event_publisher = event_publisher

    def handle(self, comando: CreateWork) -> Work:
        work = Work.create(
            partner_id=comando.partner_id,
            external_reference=comando.external_reference,
            city=comando.city,
            country=comando.country,
        )
        self._repositorio.agregar(work)
        logger.info('Work persisted: %s', work.id)

        for evento in work.eventos:
            if isinstance(evento, WorkCreated):
                integration_event = WorkCreatedIntegrationMapper.to_integration(evento)
                self._event_publisher.publish(integration_event)
        work.limpiar_eventos()

        return work
