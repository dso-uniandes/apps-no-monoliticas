from partner_rules.aplicacion.puertos.event_publisher import EventPublisher


class NoOpEventPublisher(EventPublisher):
    def publish(self, evento: object) -> None:
        return None
