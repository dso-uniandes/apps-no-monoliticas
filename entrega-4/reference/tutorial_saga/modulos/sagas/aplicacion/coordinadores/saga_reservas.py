from pydispatch import dispatcher

from aeroalpes.seedwork.aplicacion.sagas import CoordinadorOrquestacion, Transaccion, Inicio, Fin
from aeroalpes.seedwork.aplicacion.comandos import Comando, ejecutar_commando
from aeroalpes.seedwork.dominio.eventos import EventoDominio

from aeroalpes.modulos.sagas.aplicacion.comandos.cliente import RegistrarUsuario, ValidarUsuario
from aeroalpes.modulos.sagas.aplicacion.comandos.pagos import PagarReserva, RevertirPago
from aeroalpes.modulos.sagas.aplicacion.comandos.gds import ConfirmarReserva, RevertirConfirmacion
from aeroalpes.modulos.vuelos.aplicacion.comandos.crear_reserva import CrearReserva
from aeroalpes.modulos.vuelos.aplicacion.comandos.aprobar_reserva import AprobarReserva
from aeroalpes.modulos.vuelos.aplicacion.comandos.cancelar_reserva import CancelarReserva
from aeroalpes.modulos.vuelos.dominio.eventos.reservas import ReservaCreada, ReservaCancelada, ReservaAprobada, CreacionReservaFallida, AprobacionReservaFallida
from aeroalpes.modulos.sagas.dominio.eventos.pagos import ReservaPagada, PagoFallido, PagoRevertido
from aeroalpes.modulos.sagas.dominio.eventos.gds import ReservaGDSConfirmada, ConfirmacionGDSRevertida, ConfirmacionFallida
from aeroalpes.modulos.sagas.infraestructura.repositorios import RepositorioSagaLogSQLAlchemy


class CoordinadorReservas(CoordinadorOrquestacion):

    def inicializar_pasos(self):
        self.pasos = [
            Inicio(index=0),
            Transaccion(comando=CrearReserva, evento=ReservaCreada, error=CreacionReservaFallida, compensacion=CancelarReserva, exitosa=False),
            Transaccion(comando=PagarReserva, evento=ReservaPagada, error=PagoFallido, compensacion=RevertirPago, exitosa=False),
            Transaccion(comando=ConfirmarReserva, evento=ReservaGDSConfirmada, error=ConfirmacionFallida, compensacion=RevertirConfirmacion, exitosa=False),
            Transaccion(comando=AprobarReserva, evento=ReservaAprobada, error=AprobacionReservaFallida, compensacion=CancelarReserva, exitosa=False),
            Fin(),
        ]
        for i, paso in enumerate(self.pasos):
            paso.index = i

    def iniciar(self):
        if not getattr(self, 'pasos', None):
            self.inicializar_pasos()
        self.persistir_en_saga_log(self.pasos[0])
    
    def terminar(self):
        if not getattr(self, 'pasos', None):
            self.inicializar_pasos()
        self.persistir_en_saga_log(self.pasos[-1])

    def persistir_en_saga_log(self, mensaje):
        repositorio = RepositorioSagaLogSQLAlchemy()
        repositorio.agregar(mensaje)

    def procesar_evento(self, evento: EventoDominio):
        self.persistir_en_saga_log(evento)
        if not getattr(self, 'pasos', None):
            self.inicializar_pasos()
        super().procesar_evento(evento)

    def publicar_comando(self, evento: EventoDominio, tipo_comando: type):
        comando = self.construir_comando(evento, tipo_comando)
        self.persistir_en_saga_log(comando)
        ejecutar_commando(comando)

    def construir_comando(self, evento: EventoDominio, tipo_comando: type):
        id_reserva = getattr(evento, 'id_reserva', None)
        id_correlacion = getattr(evento, 'id_correlacion', None) or str(getattr(evento, 'id', ''))
        id_cliente = getattr(evento, 'id_cliente', None)
        monto = getattr(evento, 'monto', None)
        monto_vat = getattr(evento, 'monto_vat', None)
        fecha_creacion = getattr(evento, 'fecha_creacion', None)
        fecha_actualizacion = getattr(evento, 'fecha_actualizacion', None)

        if tipo_comando is PagarReserva:
            comando = PagarReserva()
            comando.id_reserva = id_reserva
            comando.id_correlacion = id_correlacion
            comando.id_cliente = id_cliente
            comando.monto = monto
            comando.monto_vat = monto_vat
            comando.fecha_creacion = fecha_creacion
            return comando

        if tipo_comando is ConfirmarReserva:
            comando = ConfirmarReserva()
            comando.id_reserva = id_reserva
            comando.id_correlacion = id_correlacion
            return comando

        if tipo_comando is AprobarReserva:
            comando = AprobarReserva()
            comando.id_reserva = id_reserva
            comando.id_correlacion = id_correlacion
            return comando

        if tipo_comando is CancelarReserva:
            comando = CancelarReserva()
            comando.id_reserva = id_reserva
            return comando

        if tipo_comando is RevertirPago:
            comando = RevertirPago()
            comando.id_reserva = id_reserva
            comando.id_correlacion = id_correlacion
            comando.monto = monto
            comando.monto_vat = monto_vat
            return comando

        if tipo_comando is RevertirConfirmacion:
            comando = RevertirConfirmacion()
            comando.id_reserva = id_reserva
            comando.id_correlacion = id_correlacion
            return comando

        if tipo_comando is CrearReserva:
            return CrearReserva(
                fecha_creacion=str(fecha_creacion or ''),
                fecha_actualizacion=str(fecha_actualizacion or fecha_creacion or ''),
                id=str(id_reserva or ''),
                itinerarios=[],
            )

        raise NotImplementedError(
            f'No se puede construir el comando {tipo_comando.__name__} a partir de {type(evento).__name__}'
        )


def oir_mensaje(evento):
    if isinstance(evento, EventoDominio):
        coordinador = CoordinadorReservas()
        coordinador.procesar_evento(evento)
    else:
        raise NotImplementedError("El mensaje no es evento de Dominio")


dispatcher.connect(oir_mensaje, signal=f'{ReservaCreada.__name__}Dominio')
dispatcher.connect(oir_mensaje, signal=f'{CreacionReservaFallida.__name__}Dominio')
dispatcher.connect(oir_mensaje, signal=f'{ReservaPagada.__name__}Dominio')
dispatcher.connect(oir_mensaje, signal=f'{PagoFallido.__name__}Dominio')
dispatcher.connect(oir_mensaje, signal=f'{ReservaGDSConfirmada.__name__}Dominio')
dispatcher.connect(oir_mensaje, signal=f'{ConfirmacionFallida.__name__}Dominio')
dispatcher.connect(oir_mensaje, signal=f'{ReservaAprobada.__name__}Dominio')
dispatcher.connect(oir_mensaje, signal=f'{AprobacionReservaFallida.__name__}Dominio')
