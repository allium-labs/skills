#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Compare Dune and Allium query results to validate conversions.

Usage:
    uv run scripts/compare_results.py dune_output.json allium_output.json
    uv run scripts/compare_results.py dune_output.csv allium_output.csv
    uv run scripts/compare_results.py dune.json allium.json --column-map tx_id=txn_id,block_time=block_timestamp

Accepts JSON (array of objects) or CSV files.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict

# Default column name mappings (Dune name → Allium name)
DEFAULT_COLUMN_MAP = {
    "tx_id": "txn_id",
    "block_time": "block_timestamp",
    "executing_account": "program_id",
    "account_arguments": "accounts",
    "amount_usd": "usd_amount",
    "token_mint_address": "mint",
}


def load_data(filepath: str) -> list[dict]:
    """Load JSON or CSV file into list of dicts."""
    ext = os.path.splitext(filepath)[1].lower()
    with open(filepath) as f:
        if ext == ".json":
            data = json.load(f)
            if isinstance(data, dict):
                # Handle Dune API response format
                data = data.get("result", {}).get("rows", data.get("rows", [data]))
            return data
        elif ext == ".csv":
            reader = csv.DictReader(f)
            return list(reader)
        else:
            # Try JSON first, then CSV
            content = f.read()
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    return data
                return data.get("result", {}).get("rows", [data])
            except json.JSONDecodeError:
                import io
                reader = csv.DictReader(io.StringIO(content))
                return list(reader)


def normalize_columns(rows: list[dict], column_map: dict[str, str]) -> list[dict]:
    """Rename columns according to the mapping."""
    normalized = []
    for row in rows:
        new_row = {}
        for k, v in row.items():
            mapped_key = column_map.get(k.lower(), k.lower())
            new_row[mapped_key] = v
        normalized.append(new_row)
    return normalized


def numeric_value(val) -> float | None:
    """Try to parse a value as numeric."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def compare_datasets(
    dune_rows: list[dict],
    allium_rows: list[dict],
    column_map: dict[str, str],
) -> dict:
    """Compare two datasets and return analysis."""
    # Normalize column names
    dune_norm = normalize_columns(dune_rows, column_map)
    allium_norm = normalize_columns(allium_rows, {})

    dune_cols = set()
    for row in dune_norm:
        dune_cols.update(row.keys())
    allium_cols = set()
    for row in allium_norm:
        allium_cols.update(row.keys())

    common_cols = dune_cols & allium_cols
    dune_only_cols = dune_cols - allium_cols
    allium_only_cols = allium_cols - dune_cols

    # Per-column stats
    col_stats = {}
    for col in sorted(common_cols):
        dune_vals = [row.get(col) for row in dune_norm]
        allium_vals = [row.get(col) for row in allium_norm]

        # Check if numeric
        dune_nums = [numeric_value(v) for v in dune_vals]
        allium_nums = [numeric_value(v) for v in allium_vals]
        dune_nums_clean = [n for n in dune_nums if n is not None]
        allium_nums_clean = [n for n in allium_nums if n is not None]

        stat: dict = {"column": col}

        if dune_nums_clean and allium_nums_clean:
            stat["type"] = "numeric"
            stat["dune_sum"] = sum(dune_nums_clean)
            stat["allium_sum"] = sum(allium_nums_clean)
            stat["dune_mean"] = stat["dune_sum"] / len(dune_nums_clean) if dune_nums_clean else 0
            stat["allium_mean"] = stat["allium_sum"] / len(allium_nums_clean) if allium_nums_clean else 0

            if stat["dune_sum"] != 0:
                stat["sum_delta_pct"] = (
                    (stat["allium_sum"] - stat["dune_sum"]) / abs(stat["dune_sum"]) * 100
                )
            else:
                stat["sum_delta_pct"] = None

            stat["dune_nulls"] = sum(1 for v in dune_nums if v is None)
            stat["allium_nulls"] = sum(1 for v in allium_nums if v is None)
        else:
            stat["type"] = "non-numeric"
            stat["dune_unique"] = len(set(str(v) for v in dune_vals if v is not None))
            stat["allium_unique"] = len(set(str(v) for v in allium_vals if v is not None))

        col_stats[col] = stat

    # Value-level matching for small datasets
    sample_mismatches = []
    if len(dune_norm) == len(allium_norm) and len(dune_norm) <= 1000:
        for i, (d_row, a_row) in enumerate(zip(dune_norm, allium_norm)):
            for col in common_cols:
                d_val = str(d_row.get(col, ""))
                a_val = str(a_row.get(col, ""))
                if d_val != a_val:
                    # Check numeric near-equality
                    d_num = numeric_value(d_row.get(col))
                    a_num = numeric_value(a_row.get(col))
                    if d_num is not None and a_num is not None:
                        if abs(d_num - a_num) < 0.01 * max(abs(d_num), abs(a_num), 1):
                            continue  # Close enough
                    sample_mismatches.append({
                        "row": i,
                        "column": col,
                        "dune": d_val[:100],
                        "allium": a_val[:100],
                    })
                    if len(sample_mismatches) >= 20:
                        break
            if len(sample_mismatches) >= 20:
                break

    return {
        "row_counts": {
            "dune": len(dune_norm),
            "allium": len(allium_norm),
            "delta": len(allium_norm) - len(dune_norm),
        },
        "columns": {
            "common": sorted(common_cols),
            "dune_only": sorted(dune_only_cols),
            "allium_only": sorted(allium_only_cols),
        },
        "column_stats": col_stats,
        "sample_mismatches": sample_mismatches,
    }


def print_report(analysis: dict):
    """Print a human-readable comparison report."""
    rc = analysis["row_counts"]
    print("=" * 60)
    print("COMPARISON REPORT")
    print("=" * 60)

    print(f"\nRow Counts:")
    print(f"  Dune:   {rc['dune']:>10,}")
    print(f"  Allium: {rc['allium']:>10,}")
    print(f"  Delta:  {rc['delta']:>+10,}")
    if rc["dune"] > 0:
        pct = rc["delta"] / rc["dune"] * 100
        print(f"  Delta%: {pct:>+10.1f}%")

    cols = analysis["columns"]
    print(f"\nColumns:")
    print(f"  Common ({len(cols['common'])}): {', '.join(cols['common'][:10])}")
    if cols["dune_only"]:
        print(f"  Dune only ({len(cols['dune_only'])}): {', '.join(cols['dune_only'][:10])}")
    if cols["allium_only"]:
        print(f"  Allium only ({len(cols['allium_only'])}): {', '.join(cols['allium_only'][:10])}")

    print(f"\nColumn Statistics:")
    print(f"  {'Column':<25} {'Type':<10} {'Dune Sum/Unique':<20} {'Allium Sum/Unique':<20} {'Delta%':<10}")
    print(f"  {'-' * 85}")
    for col, stat in sorted(analysis["column_stats"].items()):
        if stat["type"] == "numeric":
            d_val = f"{stat['dune_sum']:,.2f}"
            a_val = f"{stat['allium_sum']:,.2f}"
            delta = f"{stat['sum_delta_pct']:+.1f}%" if stat["sum_delta_pct"] is not None else "N/A"
        else:
            d_val = str(stat.get("dune_unique", "?"))
            a_val = str(stat.get("allium_unique", "?"))
            delta = ""
        print(f"  {col:<25} {stat['type']:<10} {d_val:<20} {a_val:<20} {delta:<10}")

    mismatches = analysis["sample_mismatches"]
    if mismatches:
        print(f"\nSample Mismatches ({len(mismatches)} shown):")
        for m in mismatches[:10]:
            print(f"  Row {m['row']}, {m['column']}:")
            print(f"    Dune:   {m['dune']}")
            print(f"    Allium: {m['allium']}")
    elif rc["dune"] == rc["allium"]:
        print(f"\nValue Matching: All values match (within tolerance)")

    print()


def main():
    parser = argparse.ArgumentParser(description="Compare Dune vs Allium query results")
    parser.add_argument("dune_file", help="Path to Dune results (JSON or CSV)")
    parser.add_argument("allium_file", help="Path to Allium results (JSON or CSV)")
    parser.add_argument(
        "--column-map", default="",
        help="Extra column mappings as key=value pairs, comma-separated "
             "(e.g., tx_id=txn_id,block_time=block_timestamp)"
    )
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output analysis as JSON")
    args = parser.parse_args()

    # Build column map
    column_map = dict(DEFAULT_COLUMN_MAP)
    if args.column_map:
        for pair in args.column_map.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                column_map[k.strip().lower()] = v.strip().lower()

    print(f"Loading Dune data from {args.dune_file}...", file=sys.stderr)
    dune_rows = load_data(args.dune_file)
    print(f"Loading Allium data from {args.allium_file}...", file=sys.stderr)
    allium_rows = load_data(args.allium_file)

    print(f"Column map: {column_map}", file=sys.stderr)

    analysis = compare_datasets(dune_rows, allium_rows, column_map)

    if args.output_json:
        print(json.dumps(analysis, indent=2, default=str))
    else:
        print_report(analysis)


if __name__ == "__main__":
    main()
