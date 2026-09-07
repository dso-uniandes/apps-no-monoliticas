from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from work_orchestration.infraestructura.persistencia.db import Base


class WorkModel(Base):
    __tablename__ = 'works'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    partner_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_reference: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
