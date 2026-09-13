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
                connection.execute(
                    '''
                    INSERT INTO partner_rules (
                        id, partner_id, rule_type, value, enabled,
                        fecha_creacion, fecha_actualizacion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        partner_id = excluded.partner_id,
                        rule_type = excluded.rule_type,
                        value = excluded.value,
                        enabled = excluded.enabled,
                        fecha_creacion = excluded.fecha_creacion,
                        fecha_actualizacion = excluded.fecha_actualizacion
                    ''',
                    (
                        str(entity.id), entity.partner_id.valor,
                        entity.rule_type.valor, entity.value.valor,
                        int(entity.enabled), entity.fecha_creacion.isoformat(),
                        entity.fecha_actualizacion.isoformat(),
                    ),
                )

    @staticmethod
    def _to_entity(row: sqlite3.Row) -> PartnerRule:
        return PartnerRule(
            id=UUID(row['id']), partner_id=PartnerId(row['partner_id']),
            rule_type=RuleType(row['rule_type']), value=RuleValue(row['value']),
            enabled=bool(row['enabled']),
            fecha_creacion=datetime.fromisoformat(row['fecha_creacion']),
            fecha_actualizacion=datetime.fromisoformat(row['fecha_actualizacion']),
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
