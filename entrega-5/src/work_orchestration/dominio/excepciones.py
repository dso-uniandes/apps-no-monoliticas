from seedwork.dominio.excepciones import ExcepcionDominio


class WorkInvalido(ExcepcionDominio):
    def __init__(self, mensaje: str = 'El trabajo es invalido'):
        self.mensaje = mensaje

    def __str__(self):
        return self.mensaje


class WorkNoEncontrado(ExcepcionDominio):
    def __init__(self, mensaje: str = 'El trabajo no fue encontrado'):
        self.mensaje = mensaje

    def __str__(self):
        return self.mensaje
