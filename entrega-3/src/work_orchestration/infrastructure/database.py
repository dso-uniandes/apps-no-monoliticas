import os
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from uuid import UUID
from work_orchestration.domain.model import Work, Location, WorkStatus
from work_orchestration.domain.ports import WorkRepository

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://hda:hda@localhost:5432/hda")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase): pass

class WorkRow(Base):
    __tablename__ = "works"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category: Mapped[str] = mapped_column(String(80))
    urgency: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(80))
    zone: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30))

class SqlAlchemyWorkRepository(WorkRepository):
    def add(self, work: Work) -> None:
        with SessionLocal() as s:
            s.add(WorkRow(id=str(work.id), category=work.category, urgency=work.urgency,
                          city=work.location.city, zone=work.location.zone,
                          status=work.status.value))
            s.commit()

    def get(self, work_id: UUID) -> Work | None:
        with SessionLocal() as s:
            row = s.get(WorkRow, str(work_id))
            if not row: return None
            return Work(UUID(row.id), row.category, row.urgency,
                        Location(row.city, row.zone), WorkStatus(row.status))

def init_db():
    Base.metadata.create_all(engine)
