from dataclasses import dataclass
from uuid import UUID
from work_orchestration.domain.ports import WorkRepository

@dataclass(frozen=True)
class GetWorkQuery:
    work_id: UUID

class GetWorkHandler:
    def __init__(self, repository: WorkRepository):
        self.repository = repository

    def handle(self, query: GetWorkQuery):
        return self.repository.get(query.work_id)
