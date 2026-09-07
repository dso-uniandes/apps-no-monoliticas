from seedwork.aplicacion.comandos import ComandoHandler

from work_orchestration.aplicacion.comandos.create_work import CreateWork
from work_orchestration.aplicacion.puertos.event_publisher import EventPublisher
from work_orchestration.dominio.entidades import Work
from work_orchestration.dominio.repositorios import WorkRepository


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

        for evento in work.eventos:
            self._event_publisher.publish(evento)
        work.limpiar_eventos()

        return work
