import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from uuid import UUID

from partner_rules.dominio.entidades import PartnerRule
from partner_rules.dominio.objetos_valor import PartnerId, RuleType, RuleValue
from partner_rules.dominio.repositorios import PartnerRuleRepository


class SQLitePartnerRuleRepository(PartnerRuleRepository):
    def __init__(self, database_url: str, auto_create_schema: bool = True):
        self._db_path = database_url.removeprefix('sqlite:///')
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        if auto_create_schema:
            self._create_table()

    def obtener_por_id(self, id: UUID) -> PartnerRule | None:
        with closing(sqlite3.connect(self._db_path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                'SELECT * FROM partner_rules WHERE id = ?', (str(id),)
            ).fetchone()
        return self._to_entity(row) if row is not None else None

    def obtener_por_partner(self, partner_id: str) -> list[PartnerRule]:
        with closing(sqlite3.connect(self._db_path)) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                'SELECT * FROM partner_rules WHERE partner_id = ?', (partner_id,)
            ).fetchall()
        return [self._to_entity(row) for row in rows]

    def agregar(self, entity: PartnerRule) -> None:
        with closing(sqlite3.connect(self._db_path)) as connection:
            with connection:
                columns = self._columns(connection)
                audit_values = {
                    'fecha_creacion': entity.fecha_creacion.isoformat(),
                    'fecha_actualizacion': entity.fecha_actualizacion.isoformat(),
                    'created_at': entity.fecha_creacion.isoformat(),
                    'updated_at': entity.fecha_actualizacion.isoformat(),
                }
                insert_columns = ['id', 'partner_id', 'rule_type', 'value', 'enabled']
                insert_values = [
                    str(entity.id),
                    entity.partner_id.valor,
                    entity.rule_type.valor,
                    entity.value.valor,
                    int(entity.enabled),
                ]
                for column in (
                    'fecha_creacion',
                    'fecha_actualizacion',
                    'created_at',
                    'updated_at',
                ):
                    if column in columns:
                        insert_columns.append(column)
                        insert_values.append(audit_values[column])

                update_columns = [
                    column
                    for column in insert_columns
                    if column != 'id'
                ]
                connection.execute(
                    f'''
                    INSERT INTO partner_rules ({', '.join(insert_columns)})
                    VALUES ({', '.join('?' for _ in insert_columns)})
                    ON CONFLICT(id) DO UPDATE SET
                        {', '.join(f'{column} = excluded.{column}' for column in update_columns)}
                    ''',
                    tuple(insert_values),
                )

    def actualizar(self, entity: PartnerRule) -> None:
        with closing(sqlite3.connect(self._db_path)) as connection:
            with connection:
                cursor = connection.execute(
                    '''
                    UPDATE partner_rules
                    SET partner_id = ?, rule_type = ?, value = ?, enabled = ?,
                        fecha_creacion = ?, fecha_actualizacion = ?
                    WHERE id = ?
                    ''',
                    (
                        entity.partner_id.valor,
                        entity.rule_type.valor,
                        entity.value.valor,
                        int(entity.enabled),
                        entity.fecha_creacion.isoformat(),
                        entity.fecha_actualizacion.isoformat(),
                        str(entity.id),
                    ),
                )
                if cursor.rowcount == 0:
                    raise KeyError(f'PartnerRule {entity.id} no existe')

    def eliminar(self, id: UUID) -> bool:
        with closing(sqlite3.connect(self._db_path)) as connection:
            with connection:
                cursor = connection.execute(
                    'DELETE FROM partner_rules WHERE id = ?',
                    (str(id),),
                )
                return cursor.rowcount > 0

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> PartnerRule:
        created_at = row['fecha_creacion'] if 'fecha_creacion' in row.keys() else row['created_at']
        updated_at = (
            row['fecha_actualizacion']
            if 'fecha_actualizacion' in row.keys()
            else row['updated_at']
        )
        return PartnerRule(
            id=UUID(row['id']), partner_id=PartnerId(row['partner_id']),
            rule_type=RuleType(row['rule_type']), value=RuleValue(row['value']),
            enabled=bool(row['enabled']),
            fecha_creacion=datetime.fromisoformat(created_at),
            fecha_actualizacion=datetime.fromisoformat(updated_at),
            eventos=[],
        )

    def _create_table(self) -> None:
        with closing(sqlite3.connect(self._db_path)) as connection:
            with connection:
                connection.execute(
                    '''CREATE TABLE IF NOT EXISTS partner_rules (
                        id TEXT PRIMARY KEY,
                        partner_id TEXT NOT NULL,
                        rule_type TEXT NOT NULL,
                        value TEXT NOT NULL,
                        enabled INTEGER NOT NULL CHECK (enabled IN (0, 1)),
                        fecha_creacion TEXT NOT NULL,
                        fecha_actualizacion TEXT NOT NULL
                    )'''
                )
                connection.execute(
                    'CREATE INDEX IF NOT EXISTS idx_partner_rules_partner_id '
                    'ON partner_rules (partner_id)'
                )
                self._ensure_columns(connection)

    def _ensure_columns(self, connection) -> None:
        columns = self._columns(connection)
        if 'fecha_creacion' not in columns:
            connection.execute(
                "ALTER TABLE partner_rules "
                "ADD COLUMN fecha_creacion TEXT NOT NULL DEFAULT '1970-01-01T00:00:00'"
            )
        if 'fecha_actualizacion' not in columns:
            connection.execute(
                "ALTER TABLE partner_rules "
                "ADD COLUMN fecha_actualizacion TEXT NOT NULL DEFAULT '1970-01-01T00:00:00'"
            )

    @staticmethod
    def _columns(connection) -> set[str]:
        return {
            row[1]
            for row in connection.execute('PRAGMA table_info(partner_rules)').fetchall()
        }
