from dataclasses import dataclass
from datetime import datetime
import uuid

from cliente.seedwork.dominio.eventos import EventoDominio


@dataclass
class UsuarioRegistrado(EventoDominio):
    id_usuario: uuid.UUID = None
    nombres: str = None
    apellidos: str = None
    email: str = None
    fecha_creacion: datetime = None


@dataclass
class UsuarioValidado(EventoDominio):
    id_usuario: uuid.UUID = None
    fecha_validacion: datetime = None


@dataclass
class UsuarioDesactivado(EventoDominio):
    id_usuario: uuid.UUID = None
    fecha_desactivacion: datetime = None
