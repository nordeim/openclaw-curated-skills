#!/usr/bin/env python3
"""
Fetch Toggle workflow data and print the raw JSON response.
Reads TOGGLE_API_KEY from the environment.
"""

import os
import sys
import json
import argparse
from datetime import date
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_BASE = "https://ai-x.toggle.pro/public-openclaw/workflows"


def main():
    parser = argparse.ArgumentParser(description="Fetch Toggle workflow data")
    today = date.today().isoformat()
    parser.add_argument("--from-date", default=today, help="Start date (YYYY-MM-DD), default: today")
    parser.add_argument("--to-date", default=today, help="End date (YYYY-MM-DD), default: today")
    args = parser.parse_args()

    api_key = os.environ.get("TOGGLE_API_KEY")
    if not api_key:
        print("Error: TOGGLE_API_KEY is not set.", file=sys.stderr)
        print("  export TOGGLE_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)

    url = f"{API_BASE}?fromDate={args.from_date}&toDate={args.to_date}"
    req = Request(url, headers={
        "accept": "application/json",
        "x-openclaw-api-key": api_key,
    })

    try:
        with urlopen(req) as resp:
            print(json.dumps(json.loads(resp.read().decode()), indent=2))
    except HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Request failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
