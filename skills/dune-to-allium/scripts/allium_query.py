#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.28.0",
# ]
# ///
"""Run SQL queries via the Allium Explorer API and return results.

Usage:
    uv run scripts/allium_query.py "SELECT * FROM ethereum.raw.blocks LIMIT 10"
    uv run scripts/allium_query.py --file query.sql
    uv run scripts/allium_query.py --file query.sql --json > results.json

Credentials:
    Reads API_KEY (and optionally QUERY_ID) from ~/.allium/credentials.
    If QUERY_ID is missing, creates a new query automatically and saves it.

    File format:
        API_KEY=allium_...
        QUERY_ID=abc-123-...
"""

import argparse
import json
import os
import sys
import time

import requests

API_BASE = "https://api.allium.so"
CREDENTIALS_PATH = os.path.expanduser("~/.allium/credentials")
POLL_INTERVAL = 2  # seconds
MAX_POLL_TIME = 300  # 5 minutes


def load_credentials() -> dict[str, str]:
    """Load credentials from ~/.allium/credentials."""
    creds = {}
    if not os.path.exists(CREDENTIALS_PATH):
        return creds
    with open(CREDENTIALS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                creds[key.strip()] = value.strip()
    return creds


def save_query_id(query_id: str):
    """Append QUERY_ID to credentials file."""
    with open(CREDENTIALS_PATH, "a") as f:
        f.write(f"\nQUERY_ID={query_id}\n")
    print(f"Saved QUERY_ID={query_id} to {CREDENTIALS_PATH}", file=sys.stderr)


def create_query(api_key: str) -> str:
    """Create a reusable parameterized query and return its ID."""
    resp = requests.post(
        f"{API_BASE}/api/v1/explorer/queries",
        headers={"Content-Type": "application/json", "X-API-KEY": api_key},
        json={
            "title": "Dune-to-Allium Conversion Query",
            "config": {"sql": "{{ sql_query }}", "limit": 10000},
        },
        timeout=30,
    )
    resp.raise_for_status()
    query_id = resp.json()["query_id"]
    save_query_id(query_id)
    return query_id


def run_query(api_key: str, query_id: str, sql: str) -> str:
    """Start an async query run and return the run_id."""
    resp = requests.post(
        f"{API_BASE}/api/v1/explorer/queries/{query_id}/run-async",
        headers={"Content-Type": "application/json", "X-API-KEY": api_key},
        json={"parameters": {"sql_query": sql}},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["run_id"]


def poll_status(api_key: str, run_id: str) -> str:
    """Poll until query completes. Returns final status."""
    start = time.time()
    while time.time() - start < MAX_POLL_TIME:
        resp = requests.get(
            f"{API_BASE}/api/v1/explorer/query-runs/{run_id}/status",
            headers={"X-API-KEY": api_key},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status", "unknown")
        print(f"  Status: {status}", file=sys.stderr)
        if status == "success":
            return status
        if status == "failed":
            error = resp.json().get("error", "Unknown error")
            print(f"Query failed: {error}", file=sys.stderr)
            sys.exit(1)
        time.sleep(POLL_INTERVAL)
    print("Query timed out after 5 minutes", file=sys.stderr)
    sys.exit(1)


def get_results(api_key: str, run_id: str) -> list[dict]:
    """Fetch query results as JSON."""
    resp = requests.get(
        f"{API_BASE}/api/v1/explorer/query-runs/{run_id}/results?f=json",
        headers={"X-API-KEY": api_key},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def print_table(rows: list[dict]):
    """Print results as a formatted table."""
    if not rows:
        print("(no rows)")
        return
    columns = list(rows[0].keys())
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
                s = s[: w - 3] + "..."
            vals.append(s.ljust(w))
        print(" | ".join(vals))


def main():
    parser = argparse.ArgumentParser(description="Run SQL via Allium Explorer API")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("sql", nargs="?", help="SQL query string")
    group.add_argument("--file", "-f", help="Path to .sql file")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output as JSON (default: table format)",
    )
    args = parser.parse_args()

    # Load SQL
    if args.file:
        with open(args.file) as f:
            sql = f.read().strip()
    else:
        sql = args.sql.strip()

    if not sql:
        print("Error: empty SQL query", file=sys.stderr)
        sys.exit(1)

    # Load credentials
    creds = load_credentials()
    api_key = creds.get("API_KEY")
    if not api_key:
        print(
            f"Error: API_KEY not found in {CREDENTIALS_PATH}\n"
            "Get your key at https://app.allium.so/settings/api-keys",
            file=sys.stderr,
        )
        sys.exit(1)

    query_id = creds.get("QUERY_ID")
    if not query_id:
        print("No QUERY_ID found, creating query...", file=sys.stderr)
        query_id = create_query(api_key)

    # Run
    print(f"Running query via Explorer API...", file=sys.stderr)
    run_id = run_query(api_key, query_id, sql)
    print(f"Run ID: {run_id}", file=sys.stderr)

    # Poll
    poll_status(api_key, run_id)

    # Results
    rows = get_results(api_key, run_id)
    print(f"Returned {len(rows)} rows", file=sys.stderr)

    if args.output_json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        print_table(rows)


if __name__ == "__main__":
    main()
