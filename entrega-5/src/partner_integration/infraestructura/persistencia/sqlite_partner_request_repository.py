import json
import sqlite3
from pathlib import Path
from datetime import UTC, datetime
from uuid import UUID

from partner_integration.dominio.entidades import PartnerRequest
from partner_integration.dominio.objetos_valor import ExternalReference, PartnerId
from partner_integration.dominio.repositorios import PartnerRequestRepository


class SQLitePartnerRequestRepository(PartnerRequestRepository):
    def __init__(self, database_url: str, auto_create_schema: bool = True):
        self._db_path = database_url.replace('sqlite:///', '')
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        if auto_create_schema:
            self._create_table()

    def obtener_por_id(self, id: UUID) -> PartnerRequest | None:
        with sqlite3.connect(self._db_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                'SELECT * FROM partner_requests WHERE id = ?',
                (str(id),),
            ).fetchone()

        if row is None:
            return None

        return PartnerRequest(
            id=UUID(row['id']),
            partner_id=PartnerId(row['partner_id']),
            external_reference=ExternalReference(row['external_reference']),
            payload=json.loads(row['payload']),
            normalized_payload=json.loads(row['normalized_payload'])
            if row['normalized_payload']
            else None,
            eventos=[],
        )

    def agregar(self, entity: PartnerRequest):
        with sqlite3.connect(self._db_path) as connection:
            columns = self._columns(connection)
            insert_columns = [
                'id',
                'partner_id',
                'external_reference',
                'payload',
                'normalized_payload',
            ]
            values = [
                str(entity.id),
                entity.partner_id.valor,
                entity.external_reference.valor,
                json.dumps(entity.payload),
                json.dumps(entity.normalized_payload)
                if entity.normalized_payload is not None
                else None,
            ]

            now = datetime.now(UTC).isoformat()
            for audit_column in (
                'fecha_creacion',
                'fecha_actualizacion',
                'created_at',
                'updated_at',
            ):
                if audit_column in columns:
                    insert_columns.append(audit_column)
                    values.append(now)

            placeholders = ', '.join('?' for _ in insert_columns)
            columns_sql = ', '.join(insert_columns)
            connection.execute(
                f'''
                INSERT OR REPLACE INTO partner_requests ({columns_sql})
                VALUES ({placeholders})
                ''',
                values,
            )
            connection.commit()

    def actualizar(self, entity: PartnerRequest) -> None:
        with sqlite3.connect(self._db_path) as connection:
            cursor = connection.execute(
                '''
                UPDATE partner_requests
                SET partner_id = ?, external_reference = ?, payload = ?,
                    normalized_payload = ?
                WHERE id = ?
                ''',
                (
                    entity.partner_id.valor,
                    entity.external_reference.valor,
                    json.dumps(entity.payload),
                    json.dumps(entity.normalized_payload)
                    if entity.normalized_payload is not None
                    else None,
                    str(entity.id),
                ),
            )
            connection.commit()
            if cursor.rowcount == 0:
                raise KeyError(f'PartnerRequest {entity.id} no existe')

    def _columns(self, connection: sqlite3.Connection) -> set[str]:
        rows = connection.execute('PRAGMA table_info(partner_requests)').fetchall()
        return {row[1] for row in rows}

    def eliminar(self, id: UUID) -> bool:
        with sqlite3.connect(self._db_path) as connection:
            cursor = connection.execute(
                'DELETE FROM partner_requests WHERE id = ?',
                (str(id),),
            )
            connection.commit()
            return cursor.rowcount > 0

    def _create_table(self) -> None:
        with sqlite3.connect(self._db_path) as connection:
            connection.execute(
                '''
                CREATE TABLE IF NOT EXISTS partner_requests (
                    id TEXT PRIMARY KEY,
                    partner_id TEXT NOT NULL,
                    external_reference TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    normalized_payload TEXT
                )
                '''
            )
            connection.commit()
