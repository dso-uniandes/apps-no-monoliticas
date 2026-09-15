#!/usr/bin/env python3
"""Publish one revision of WorkCreated using its real Pulsar Avro schema."""

from __future__ import annotations

import argparse
import time
from uuid import uuid4

import pulsar
from pulsar.schema import AvroSchema

from published_language.v1.work_created import WorkCreatedV1
from published_language.v2.work_created import WorkCreatedV2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pulsar-url', default='pulsar://broker:6650')
    parser.add_argument('--listener-name', default='internal')
    parser.add_argument('--topic', required=True)
    parser.add_argument('--version', choices=('1', '2'), required=True)
    parser.add_argument('--messages', type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    record_type = WorkCreatedV1 if args.version == '1' else WorkCreatedV2
    client = pulsar.Client(args.pulsar_url, listener_name=args.listener_name)
    producer = client.create_producer(
        args.topic,
        schema=AvroSchema(record_type),
        batching_enabled=True,
    )
    run_id = uuid4().hex
    occurred_at = int(time.time() * 1000)

    for index in range(args.messages):
        values = {
            'event_id': f'deploy-event-v{args.version}-{run_id}-{index}',
            'occurred_at': occurred_at,
            'schema_version': args.version,
            'work_id': f'deploy-v{args.version}-{run_id}-{index}',
            'partner_id': 'deployability-experiment',
            'external_reference': f'compatibility-v{args.version}-{index}',
            'status': 'CREATED',
            'city': 'Bogota',
            'country': 'CO',
        }
        if args.version == '2':
            values.update(region='LATAM-NORTH', priority='HIGH')
        producer.send(record_type(**values))

    producer.close()
    client.close()
    print(f'Published {args.messages} WorkCreatedV{args.version} messages')


if __name__ == '__main__':
    main()
