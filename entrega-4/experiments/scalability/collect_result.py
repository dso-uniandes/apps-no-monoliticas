#!/usr/bin/env python3
"""Measure the percentage of queued messages acknowledged after 60 seconds."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.request import urlopen


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--admin-url', default='http://localhost:8080')
    parser.add_argument('--topic-name', required=True)
    parser.add_argument('--subscription', required=True)
    parser.add_argument('--messages', type=int, default=10_000)
    parser.add_argument('--consumers', type=int, required=True)
    parser.add_argument('--started-at', type=float, required=True)
    parser.add_argument('--duration', type=int, default=60)
    parser.add_argument('--output', type=Path, required=True)
    return parser.parse_args()


def subscription_backlog(admin_url: str, topic_name: str, subscription: str) -> int:
    url = f'{admin_url}/admin/v2/persistent/public/default/{topic_name}/stats'
    with urlopen(url, timeout=10) as response:
        stats = json.load(response)
    return int(stats['subscriptions'][subscription]['msgBacklog'])


def main() -> None:
    args = parse_args()
    remaining = args.started_at + args.duration - time.time()
    if remaining > 0:
        time.sleep(remaining)

    backlog = subscription_backlog(
        args.admin_url, args.topic_name, args.subscription
    )
    processed = max(0, min(args.messages, args.messages - backlog))
    percentage = round(processed * 100 / args.messages, 2)
    result = {
        'scenario': 'provider_matching_scalability',
        'messages': args.messages,
        'consumers': args.consumers,
        'duration_seconds': args.duration,
        'processed': processed,
        'processed_percentage': percentage,
        'required_percentage': 95.0,
        'result': 'PASS' if percentage >= 95.0 else 'FAIL',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

