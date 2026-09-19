#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from urllib.request import urlopen


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--admin-url', default='http://localhost:18080')
    parser.add_argument('--topic-name', required=True)
    parser.add_argument('--subscription', required=True)
    parser.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()
    url = f'{args.admin_url}/admin/v2/persistent/public/default/{args.topic_name}/stats'
    deadline = time.time() + args.timeout

    while time.time() < deadline:
        try:
            with urlopen(url, timeout=5) as response:
                stats = json.load(response)
            subscription = stats.get('subscriptions', {}).get(args.subscription)
            if subscription is not None and int(subscription['msgBacklog']) == 0:
                return
        except Exception:
            pass
        time.sleep(1)
    raise SystemExit('Timed out waiting for the V1 consumer to clear the backlog')


if __name__ == '__main__':
    main()
