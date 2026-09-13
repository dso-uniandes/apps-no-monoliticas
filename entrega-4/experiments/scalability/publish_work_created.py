#!/usr/bin/env python3
"""Create a durable subscription and enqueue WorkCreatedV1 events."""

from __future__ import annotations

import argparse
import time
from uuid import uuid4

import pulsar
from pulsar.schema import AvroSchema

from published_language.v1.work_created import WorkCreatedV1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pulsar-url', default='pulsar://localhost:6650')
    parser.add_argument('--listener-name', default='external')
    parser.add_argument('--topic', required=True)
    parser.add_argument('--subscription', required=True)
    parser.add_argument('--messages', type=int, default=10_000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = pulsar.Client(args.pulsar_url, listener_name=args.listener_name)
    schema = AvroSchema(WorkCreatedV1)

    # The subscription must exist before publishing so all messages form the queue.
    consumer = client.subscribe(
        args.topic,
        args.subscription,
        consumer_type=pulsar.ConsumerType.Shared,
        initial_position=pulsar.InitialPosition.Earliest,
        schema=schema,
    )
    consumer.close()

    producer = client.create_producer(args.topic, schema=schema, batching_enabled=True)
    prefix = uuid4().hex
    occurred_at = int(time.time() * 1000)
    for index in range(args.messages):
        work_id = f'{prefix}-{index}'
        producer.send_async(
            WorkCreatedV1(
                event_id=f'event-{work_id}',
                occurred_at=occurred_at,
                schema_version='1',
                work_id=work_id,
                partner_id='scalability-experiment',
                external_reference=f'load-{index}',
                status='CREATED',
                city='Bogota',
                country='CO',
            ),
            callback=lambda result, message_id: None,
        )
    producer.flush()
    producer.close()
    client.close()
    print(f'Published {args.messages} WorkCreatedV1 messages')


if __name__ == '__main__':
    main()
