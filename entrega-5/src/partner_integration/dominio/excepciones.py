from seedwork.dominio.excepciones import ExcepcionDominio


class PartnerRequestInvalido(ExcepcionDominio):
    def __init__(self, mensaje: str = 'La solicitud del partner es invalida'):
        self.mensaje = mensaje

    def __str__(self):
        return self.mensaje
