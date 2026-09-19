import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from uuid import UUID, uuid4

from aeroalpes.config.db import db
from aeroalpes.modulos.sagas.dominio.repositorios import RepositorioSagaLog
from aeroalpes.seedwork.aplicacion.comandos import Comando
from aeroalpes.seedwork.aplicacion.sagas import Paso
from aeroalpes.seedwork.dominio.eventos import EventoDominio
from .dto import SagaLog


def _serializar_mensaje(mensaje) -> str:
    if mensaje is None:
        return '{}'

    if isinstance(mensaje, type):
        return json.dumps({'clase': mensaje.__name__})

    datos = {'clase': type(mensaje).__name__}

    if is_dataclass(mensaje):
        for campo in fields(mensaje):
            valor = getattr(mensaje, campo.name)
            datos[campo.name] = valor.__name__ if isinstance(valor, type) else valor
        return json.dumps(datos, default=str)

    if hasattr(mensaje, '__dict__'):
        for nombre, valor in vars(mensaje).items():
            if nombre.startswith('_'):
                continue
            datos[nombre] = valor.__name__ if isinstance(valor, type) else valor
        return json.dumps(datos, default=str)

    for attr in ('id_reserva', 'id_correlacion', 'id', 'index', 'monto', 'monto_vat', 'id_cliente'):
        if hasattr(mensaje, attr):
            valor = getattr(mensaje, attr)
            if not callable(valor):
                datos[attr] = valor
    return json.dumps(datos, default=str)


def _tipo_mensaje(mensaje) -> str:
    if isinstance(mensaje, EventoDominio):
        return 'evento'
    if isinstance(mensaje, Paso):
        return 'paso'
    if isinstance(mensaje, Comando) or mensaje.__class__.__name__.endswith(('Reserva', 'Pago', 'Confirmacion', 'Usuario')):
        return 'comando'
    return 'mensaje'


class RepositorioSagaLogSQLAlchemy(RepositorioSagaLog):

    def obtener_por_id(self, id: UUID):
        return db.session.query(SagaLog).filter_by(id=str(id)).one_or_none()

    def obtener_todos(self) -> list:
        return db.session.query(SagaLog).all()

    def agregar(self, mensaje):
        registro = SagaLog()
        registro.id = str(uuid4())
        registro.id_correlacion = str(getattr(mensaje, 'id_correlacion', None) or getattr(mensaje, 'id', '') or '')
        registro.id_reserva = str(getattr(mensaje, 'id_reserva', None) or '')
        registro.fecha = getattr(mensaje, 'fecha_evento', None) or getattr(mensaje, 'fecha_creacion', None) or datetime.utcnow()
        registro.tipo_mensaje = _tipo_mensaje(mensaje)
        registro.nombre = type(mensaje).__name__
        registro.contenido = _serializar_mensaje(mensaje)

        db.session.add(registro)
        db.session.commit()

    def actualizar(self, entity):
        raise NotImplementedError

    def eliminar(self, entity_id: UUID):
        raise NotImplementedError
