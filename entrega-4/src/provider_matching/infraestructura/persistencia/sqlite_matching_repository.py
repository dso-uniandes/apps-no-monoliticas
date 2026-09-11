import sqlite3
from pathlib import Path
from uuid import UUID

from provider_matching.dominio.entidades import Matching
from provider_matching.dominio.objetos_valor import MatchingStatus, ProviderId, WorkId
from provider_matching.dominio.repositorios import MatchingRepository


class SQLiteMatchingRepository(MatchingRepository):
    def __init__(self, database_url: str, auto_create_schema: bool = True):
        self._db_path = database_url.replace('sqlite:///', '')
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        if auto_create_schema:
            self._create_table()

    def obtener_por_id(self, id: UUID) -> Matching | None:
        with sqlite3.connect(self._db_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                'SELECT * FROM matchings WHERE id = ?',
                (str(id),),
            ).fetchone()

        if row is None:
            return None

        return Matching(
            id=UUID(row['id']),
            work_id=WorkId(row['work_id']),
            status=MatchingStatus(row['status']),
            provider_id=ProviderId(row['provider_id'])
            if row['provider_id']
            else None,
            eventos=[],
        )

    def agregar(self, entity: Matching):
        with sqlite3.connect(self._db_path) as connection:
            connection.execute(
                '''
                INSERT OR REPLACE INTO matchings (
                    id, work_id, status, provider_id
                ) VALUES (?, ?, ?, ?)
                ''',
                (
                    str(entity.id),
                    entity.work_id.valor,
                    entity.status.valor,
                    entity.provider_id.valor if entity.provider_id else None,
                ),
            )
            connection.commit()

    def _create_table(self) -> None:
        with sqlite3.connect(self._db_path) as connection:
            connection.execute(
                '''
                CREATE TABLE IF NOT EXISTS matchings (
                    id TEXT PRIMARY KEY,
                    work_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    provider_id TEXT
                )
                '''
            )
            connection.commit()
