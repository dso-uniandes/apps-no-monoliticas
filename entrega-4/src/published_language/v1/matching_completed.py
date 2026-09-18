from pulsar.schema import Long, Record, String


class MatchingCompletedV1(Record):
    event_id = String()
    occurred_at = Long()
    schema_version = String(default='1')
    matching_id = String()
    work_id = String()
    external_reference = String()
    provider_id = String()
    status = String()
