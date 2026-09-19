from seedwork.dominio.excepciones import ExcepcionDominio


class MatchingInvalido(ExcepcionDominio):
    def __init__(self, mensaje: str = 'El matching es invalido'):
        self.mensaje = mensaje

    def __str__(self):
        return self.mensaje
