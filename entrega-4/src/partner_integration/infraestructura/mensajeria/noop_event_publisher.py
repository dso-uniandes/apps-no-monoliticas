from seedwork.dominio.eventos import EventoDominio

from partner_integration.aplicacion.puertos.event_publisher import EventPublisher


class NoOpEventPublisher(EventPublisher):
    def publish(self, evento: EventoDominio) -> None:
        return None
