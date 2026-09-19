from pulsar.schema import Long, Record, String


class WorkCreatedV1(Record):
    event_id = String()
    occurred_at = Long()
    schema_version = String(default='1')
    work_id = String()
    partner_id = String()
    external_reference = String()
    status = String()
    city = String()
    country = String()
