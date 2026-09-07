from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def init_db(database_url: str, auto_create_schema: bool = True) -> None:
    global _engine, _SessionLocal

    _engine = create_engine(database_url, pool_pre_ping=True)
    _SessionLocal = sessionmaker(
        bind=_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    if auto_create_schema:
        # Importa modelos para registrar metadata antes de create_all.
        from work_orchestration.infraestructura.persistencia import modelos  # noqa: F401

        Base.metadata.create_all(bind=_engine)


def get_session_factory():
    if _SessionLocal is None:
        raise RuntimeError('La base de datos no ha sido inicializada')
    return _SessionLocal


def dispose_db() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
