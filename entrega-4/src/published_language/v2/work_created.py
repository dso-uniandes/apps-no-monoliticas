from pulsar.schema import Long, Record, String


class WorkCreatedV1(Record):
    """Second compatible revision of the WorkCreated Avro record.

    Avro uses the record fullname during schema resolution.  Keeping the
    logical name ``WorkCreatedV1`` lets existing V1 readers resolve this
    writer schema while the Python alias below identifies the revision used
    by new producers.
    """

    event_id = String()
    occurred_at = Long()
    schema_version = String(default='2')
    work_id = String()
    partner_id = String()
    external_reference = String()
    status = String()
    city = String()
    country = String()
    region = String(default='', required=True, required_default=True)
    priority = String(default='NORMAL', required=True, required_default=True)


WorkCreatedV2 = WorkCreatedV1
