from cliente.seedwork.aplicacion.queries import Query, QueryHandler, ResultadoQuery
import uuid

class ObtenerUsuario(Query):
    id_usuario: uuid.UUID

class ObtenerUsuarioHandler(QueryHandler):

    def handle() -> ResultadoQuery:
        ...
