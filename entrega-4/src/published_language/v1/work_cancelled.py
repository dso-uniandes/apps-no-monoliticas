from pulsar.schema import Long, Record, String


class WorkCancelledV1(Record):
    event_id = String()
    occurred_at = Long()
    schema_version = String(default='1')
    work_id = String()
    external_reference = String()
    reason = String()
    status = String()
