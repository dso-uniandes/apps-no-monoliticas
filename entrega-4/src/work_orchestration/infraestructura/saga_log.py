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

    def list_sagas(self, limit: int = 50) -> list[dict]:
        """Ultimas sagas registradas, de la mas reciente a la mas antigua.

        Devuelve los pasos de cada una para que el consumidor derive el estado
        con la misma logica que usa en la consulta individual.
        """
        with sqlite3.connect(self._db_path) as connection:
            connection.row_factory = sqlite3.Row
            referencias = connection.execute(
                """
                SELECT external_reference,
                       MAX(id) AS last_id,
                       MAX(created_at) AS updated_at,
                       COUNT(*) AS steps_count
                FROM saga_log
                GROUP BY external_reference
                ORDER BY last_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            sagas = []
            for fila in referencias:
                pasos = connection.execute(
                    """
                    SELECT step, status, detail, created_at
                    FROM saga_log
                    WHERE external_reference = ?
                    ORDER BY id
                    """,
                    (fila['external_reference'],),
                ).fetchall()
                sagas.append(
                    {
                        'external_reference': fila['external_reference'],
                        'updated_at': fila['updated_at'],
                        'steps_count': fila['steps_count'],
                        'steps': [dict(paso) for paso in pasos],
                    }
                )

        return sagas

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
