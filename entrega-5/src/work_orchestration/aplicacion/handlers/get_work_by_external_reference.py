from seedwork.aplicacion.queries import QueryHandler, ResultadoQuery

from work_orchestration.aplicacion.queries.get_work_by_external_reference import (
    GetWorkByExternalReference,
)
from work_orchestration.dominio.excepciones import WorkNoEncontrado
from work_orchestration.dominio.repositorios import WorkRepository


class GetWorkByExternalReferenceHandler(QueryHandler):
    def __init__(self, repositorio: WorkRepository):
        self._repositorio = repositorio

    def handle(self, query: GetWorkByExternalReference) -> ResultadoQuery:
        work = self._repositorio.obtener_por_external_reference(query.external_reference)
        if work is None:
            raise WorkNoEncontrado(
                f'Work con external_reference {query.external_reference} no encontrado'
            )
        return ResultadoQuery(resultado=work)
