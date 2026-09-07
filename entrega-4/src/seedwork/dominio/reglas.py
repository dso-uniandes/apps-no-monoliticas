from abc import ABC, abstractmethod


class ReglaNegocio(ABC):
    __mensaje: str = 'La regla de negocio es invalida'

    def __init__(self, mensaje):
        self.__mensaje = mensaje

    def mensaje_error(self) -> str:
        return self.__mensaje

    @abstractmethod
    def es_valido(self) -> bool:
        ...

    def __str__(self):
        return f"{self.__class__.__name__} - {self.__mensaje}"
