#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.28.0",
# ]
# ///
"""Fetch results from Dune Analytics saved queries via API.

Usage:
    uv run scripts/dune_query.py QUERY_ID [--json]
    uv run scripts/dune_query.py 12345 --json > output.json

Notes:
    - Free tier only supports fetching results of saved queries by ID
    - Free tier does NOT support executing arbitrary SQL
    - Set DUNE_API_KEY in .env file
"""

import argparse
import json
import os
import sys

import requests

DUNE_API_BASE = "https://api.dune.com/api/v1"


def load_env(env_path: str = ".env"):
    """Load .env file into environment."""
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def get_query_results(query_id: int, api_key: str) -> dict:
    """Fetch the latest results for a saved Dune query."""
    url = f"{DUNE_API_BASE}/query/{query_id}/results"
    headers = {"X-Dune-API-Key": api_key}

    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Fetch Dune saved query results")
    parser.add_argument("query_id", type=int, help="Dune saved query ID")
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output as JSON (default: table format)")
    parser.add_argument("--env", default=None,
                        help="Path to .env file (default: project .env)")
    args = parser.parse_args()

    # Load .env from current working directory (project root)
    env_path = args.env or os.path.join(os.getcwd(), ".env")
    load_env(env_path)

    api_key = os.environ.get("DUNE_API_KEY")
    if not api_key:
        print("Error: DUNE_API_KEY not found in environment or .env file", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching results for Dune query #{args.query_id}...", file=sys.stderr)

    try:
        result = get_query_results(args.query_id, api_key)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Error: Query #{args.query_id} not found or not accessible", file=sys.stderr)
        elif e.response.status_code == 401:
            print("Error: Invalid DUNE_API_KEY", file=sys.stderr)
        elif e.response.status_code == 429:
            print("Error: Rate limited. Free tier allows limited requests.", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract rows from response
    rows = result.get("result", {}).get("rows", [])
    metadata = result.get("result", {}).get("metadata", {})
    columns = metadata.get("column_names", [])

    print(f"Returned {len(rows)} rows, {len(columns)} columns", file=sys.stderr)
    if metadata.get("row_count") is not None:
        print(f"Total rows in result set: {metadata['row_count']}", file=sys.stderr)

    execution_id = result.get("execution_id", "unknown")
    print(f"Execution ID: {execution_id}", file=sys.stderr)

    if args.output_json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        if not rows:
            print("(no rows)")
            return

        # Derive columns from first row if metadata didn't provide them
        if not columns:
            columns = list(rows[0].keys())

        # Table format
        widths = [len(c) for c in columns]
        for row in rows:
            for i, col in enumerate(columns):
                val_len = len(str(row.get(col, "NULL")))
                widths[i] = max(widths[i], min(val_len, 60))
        widths = [min(w, 60) for w in widths]

        header = " | ".join(c[:w].ljust(w) for c, w in zip(columns, widths))
        print(header)
        print("-" * len(header))
        for row in rows:
            vals = []
            for col, w in zip(columns, widths):
                s = str(row.get(col, "NULL"))
                if len(s) > w:
                    s = s[:w - 3] + "..."
                vals.append(s.ljust(w))
            print(" | ".join(vals))


if __name__ == "__main__":
    main()
