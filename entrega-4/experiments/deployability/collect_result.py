#!/usr/bin/env python3
"""Build quantitative evidence from Pulsar stats and consumer logs."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.request import urlopen


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--admin-url', default='http://localhost:18080')
    parser.add_argument('--topic-name', required=True)
    parser.add_argument('--subscription', required=True)
    parser.add_argument('--messages-per-version', type=int, default=100)
    parser.add_argument('--consumer-log', type=Path, required=True)
    parser.add_argument('--consumer-checksum-before', required=True)
    parser.add_argument('--consumer-checksum-after', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=60)
    return parser.parse_args()


def topic_stats(admin_url: str, topic_name: str) -> dict:
    url = f'{admin_url}/admin/v2/persistent/public/default/{topic_name}/stats'
    with urlopen(url, timeout=10) as response:
        return json.load(response)


def wait_until_consumed(args: argparse.Namespace) -> dict:
    deadline = time.time() + args.timeout
    latest = {}
    while time.time() < deadline:
        latest = topic_stats(args.admin_url, args.topic_name)
        subscription = latest.get('subscriptions', {}).get(args.subscription, {})
        if int(subscription.get('msgBacklog', -1)) == 0:
            return latest
        time.sleep(1)
    return latest


def main() -> None:
    args = parse_args()
    stats = wait_until_consumed(args)
    subscription = stats.get('subscriptions', {}).get(args.subscription, {})
    backlog = int(subscription.get('msgBacklog', -1))
    log = args.consumer_log.read_text(encoding='utf-8', errors='replace')
    v1_processed = log.count('WorkCreatedV1 received: deploy-v1-')
    v2_processed = log.count('WorkCreatedV1 received: deploy-v2-')
    processing_errors = log.count('Error procesando WorkCreatedV1')
    loop_errors = log.count('Fallo el loop del consumidor WorkCreatedV1')
    consumer_unchanged = (
        args.consumer_checksum_before == args.consumer_checksum_after
    )
    expected = args.messages_per_version
    passed = (
        v1_processed == expected
        and v2_processed == expected
        and backlog == 0
        and processing_errors == 0
        and loop_errors == 0
        and consumer_unchanged
    )
    result = {
        'scenario': 'work_created_schema_compatibility',
        'v1_published': expected,
        'v1_processed_by_v1_consumer': v1_processed,
        'v2_published': expected,
        'v2_processed_by_v1_consumer': v2_processed,
        'final_backlog': backlog,
        'deserialization_or_processing_errors': processing_errors + loop_errors,
        'consumer_checksum_before': args.consumer_checksum_before,
        'consumer_checksum_after': args.consumer_checksum_after,
        'consumer_code_changes': 0 if consumer_unchanged else 1,
        'result': 'PASS' if passed else 'FAIL',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
