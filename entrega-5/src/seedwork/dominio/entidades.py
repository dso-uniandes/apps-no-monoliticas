from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .eventos import EventoDominio
from .mixins import ValidarReglasMixin


@dataclass
class Entidad:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgregacionRaiz(Entidad, ValidarReglasMixin):
    eventos: list[EventoDominio] = field(default_factory=list)

    def agregar_evento(self, evento: EventoDominio):
        self.eventos.append(evento)

    def limpiar_eventos(self):
        self.eventos = list()
