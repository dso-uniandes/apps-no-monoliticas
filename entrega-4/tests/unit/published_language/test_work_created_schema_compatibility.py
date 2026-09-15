import io
import json

from fastavro import schemaless_reader, schemaless_writer
from pulsar.schema import AvroSchema

from published_language.v1.work_created import WorkCreatedV1
from published_language.v2.work_created import WorkCreatedV2


BASE_VALUES = {
    'event_id': 'event-1',
    'occurred_at': 1,
    'work_id': 'work-1',
    'partner_id': 'partner-1',
    'external_reference': 'external-1',
    'status': 'CREATED',
    'city': 'Bogota',
    'country': 'CO',
}


def _schema(record_type) -> dict:
    return json.loads(AvroSchema(record_type).schema_info().schema())


def _round_trip(writer_type, reader_type, value) -> dict:
    writer = AvroSchema(writer_type)
    buffer = io.BytesIO()
    schemaless_writer(buffer, _schema(writer_type), writer.encode_dict(value.__dict__))
    buffer.seek(0)
    return schemaless_reader(buffer, _schema(writer_type), _schema(reader_type))


def test_v1_reader_can_read_v2_and_ignore_added_fields():
    value = WorkCreatedV2(
        **BASE_VALUES,
        schema_version='2',
        region='LATAM-NORTH',
        priority='HIGH',
    )
    decoded = _round_trip(WorkCreatedV2, WorkCreatedV1, value)
    assert decoded['work_id'] == 'work-1'
    assert decoded['schema_version'] == '2'
    assert 'region' not in decoded
    assert 'priority' not in decoded


def test_v2_reader_can_read_v1_using_defaults():
    value = WorkCreatedV1(**BASE_VALUES, schema_version='1')
    decoded = _round_trip(WorkCreatedV1, WorkCreatedV2, value)
    assert decoded['region'] == ''
    assert decoded['priority'] == 'NORMAL'
    assert _schema(WorkCreatedV1)['name'] == _schema(WorkCreatedV2)['name']
