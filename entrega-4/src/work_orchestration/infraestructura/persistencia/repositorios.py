from uuid import UUID

from work_orchestration.dominio.entidades import Work
from work_orchestration.dominio.repositorios import WorkRepository
from work_orchestration.infraestructura.persistencia.mappers import WorkPersistenceMapper
from work_orchestration.infraestructura.persistencia.modelos import WorkModel


class SQLAlchemyWorkRepository(WorkRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def obtener_por_id(self, id: UUID) -> Work | None:
        session = self._session_factory()
        try:
            model = session.get(WorkModel, str(id))
            if model is None:
                return None
            return WorkPersistenceMapper.to_domain(model)
        finally:
            session.close()

    def agregar(self, entity: Work):
        session = self._session_factory()
        try:
            model = WorkPersistenceMapper.to_model(entity)
            session.add(model)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def actualizar(self, entity: Work) -> None:
        session = self._session_factory()
        try:
            model = session.get(WorkModel, str(entity.id))
            if model is None:
                raise KeyError(f'Work {entity.id} no existe')
            model.partner_id = entity.partner_id.valor
            model.external_reference = entity.external_reference.valor
            model.status = entity.status.valor
            model.city = entity.location.city
            model.country = entity.location.country
            model.created_at = entity.fecha_creacion
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def eliminar(self, id: UUID) -> bool:
        session = self._session_factory()
        try:
            model = session.get(WorkModel, str(id))
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
