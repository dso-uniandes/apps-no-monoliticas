import sqlite3
from pathlib import Path


class SagaLog:
    def __init__(self, database_url: str, auto_create_schema: bool = True):
        self._db_path = database_url.replace('sqlite:///', '')
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        if auto_create_schema:
            self._create_table()

    def add_step(
        self,
        external_reference: str,
        step: str,
        status: str,
        detail: str = '',
    ) -> None:
        with sqlite3.connect(self._db_path) as connection:
            connection.execute(
                '''
                INSERT INTO saga_log (external_reference, step, status, detail)
                VALUES (?, ?, ?, ?)
                ''',
                (external_reference, step, status, detail),
            )
            connection.commit()

    def get_steps(self, external_reference: str) -> list[dict]:
        with sqlite3.connect(self._db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                '''
                SELECT id, external_reference, step, status, detail, created_at
                FROM saga_log
                WHERE external_reference = ?
                ORDER BY id
                ''',
                (external_reference,),
            ).fetchall()

        return [dict(row) for row in rows]

    def _create_table(self) -> None:
        with sqlite3.connect(self._db_path) as connection:
            connection.execute(
                '''
                CREATE TABLE IF NOT EXISTS saga_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    external_reference TEXT NOT NULL,
                    step TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )
            connection.commit()
