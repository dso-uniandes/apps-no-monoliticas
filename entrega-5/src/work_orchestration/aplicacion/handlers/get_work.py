from seedwork.aplicacion.queries import QueryHandler, ResultadoQuery

from work_orchestration.aplicacion.queries.get_work import GetWork
from work_orchestration.dominio.excepciones import WorkNoEncontrado
from work_orchestration.dominio.repositorios import WorkRepository


class GetWorkHandler(QueryHandler):
    def __init__(self, repositorio: WorkRepository):
        self._repositorio = repositorio

    def handle(self, query: GetWork) -> ResultadoQuery:
        work = self._repositorio.obtener_por_id(query.work_id)
        if work is None:
            raise WorkNoEncontrado(f'Work {query.work_id} no encontrado')
        return ResultadoQuery(resultado=work)
