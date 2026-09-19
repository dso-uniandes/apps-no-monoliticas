from seedwork.dominio.eventos import EventoDominio

from provider_matching.aplicacion.puertos.event_publisher import EventPublisher


class NoOpEventPublisher(EventPublisher):
    def publish(self, evento: EventoDominio) -> None:
        return None
