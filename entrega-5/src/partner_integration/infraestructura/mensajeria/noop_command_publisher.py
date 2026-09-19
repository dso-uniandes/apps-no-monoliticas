from partner_integration.aplicacion.puertos.command_publisher import CommandPublisher


class NoOpCommandPublisher(CommandPublisher):
    def publish(self, comando: object) -> None:
        return None
