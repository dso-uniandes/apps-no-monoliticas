from uuid import UUID

from work_orchestration.dominio.entidades import Work
from work_orchestration.infraestructura.persistencia.modelos import WorkModel


class WorkPersistenceMapper:
    @staticmethod
    def to_model(work: Work) -> WorkModel:
        return WorkModel(
            id=str(work.id),
            partner_id=work.partner_id.valor,
            external_reference=work.external_reference.valor,
            status=work.status.valor,
            city=work.location.city,
            country=work.location.country,
            created_at=work.fecha_creacion,
        )

    @staticmethod
    def to_domain(model: WorkModel) -> Work:
        return Work.rehydrate(
            id=UUID(model.id),
            partner_id=model.partner_id,
            external_reference=model.external_reference,
            status=model.status,
            city=model.city,
            country=model.country,
            created_at=model.created_at,
        )
