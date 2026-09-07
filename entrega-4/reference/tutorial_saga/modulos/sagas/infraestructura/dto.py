from aeroalpes.config.db import db


class SagaLog(db.Model):
    __tablename__ = "saga_log"
    id = db.Column(db.String(40), primary_key=True)
    id_correlacion = db.Column(db.String(40), nullable=True)
    id_reserva = db.Column(db.String(40), nullable=True)
    fecha = db.Column(db.DateTime, nullable=False)
    tipo_mensaje = db.Column(db.String(40), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
