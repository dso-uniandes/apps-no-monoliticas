from abc import ABC, abstractmethod


class Comando:
    ...


class ComandoHandler(ABC):
    @abstractmethod
    def handle(self, comando: Comando):
        raise NotImplementedError()
