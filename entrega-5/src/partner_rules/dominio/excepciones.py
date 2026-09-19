from seedwork.dominio.excepciones import ExcepcionDominio


class PartnerRuleInvalida(ExcepcionDominio):
    def __init__(self, mensaje: str = 'La regla del partner es invalida'):
        self.mensaje = mensaje

    def __str__(self):
        return self.mensaje
