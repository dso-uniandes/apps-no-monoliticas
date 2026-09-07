from seedwork.dominio.eventos import EventoDominio

from work_orchestration.aplicacion.puertos.event_publisher import EventPublisher


class NoOpEventPublisher(EventPublisher):
    def publish(self, evento: EventoDominio) -> None:
        return None
