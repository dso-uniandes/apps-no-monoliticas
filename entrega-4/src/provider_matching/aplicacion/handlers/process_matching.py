from seedwork.aplicacion.comandos import ComandoHandler

from provider_matching.aplicacion.comandos.process_matching import ProcessMatching
from provider_matching.aplicacion.puertos.event_publisher import EventPublisher
from provider_matching.dominio.entidades import Matching
from provider_matching.dominio.repositorios import MatchingRepository


class ProcessMatchingHandler(ComandoHandler):
    def __init__(
        self,
        repositorio: MatchingRepository,
        event_publisher: EventPublisher,
    ):
        self._repositorio = repositorio
        self._event_publisher = event_publisher

    def handle(self, comando: ProcessMatching) -> Matching:
        matching = Matching.crear(work_id=comando.work_id)

        # Logica minima: asigna un provider recibido por contrato o un placeholder.
        provider_id = comando.candidate_provider_id or 'provider-pending'
        matching.completar(provider_id)

        self._repositorio.agregar(matching)

        for evento in matching.eventos:
            self._event_publisher.publish(evento)
        matching.limpiar_eventos()

        return matching
