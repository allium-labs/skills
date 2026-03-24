---
name: allium-x402-explorer
description: >-
  Run SQL queries on historical blockchain data across 150+ chains.
  Use for long-term analysis, cross-chain metrics, custom aggregations.
  Data freshness: minutes to hours (not realtime).
---

# Allium Explorer (SQL Analytics)

Use Explorer when the user needs **historical analysis, cross-chain comparisons, or custom aggregations** — anything that requires SQL. Think Snowflake-style analytical queries: powerful, flexible, not realtime.

**When to use Explorer vs Developer:**

| Explorer (this skill)                                    | Developer (x402-developer.md)                   |
| -------------------------------------------------------- | ------------------------------------------------ |
| "How did gas prices trend over the last 6 months?"       | "What's the current gas price on Ethereum?"      |
| "Top 10 wallets by volume on Arbitrum last quarter"      | "Show my wallet balance"                         |
| "Compare daily active addresses across all L2s"          | "What's ETH worth right now?"                    |
| "Find all transfers over $1M on Base this week"          | "Get recent transactions for this wallet"        |
| "What % of Solana transactions are DEX swaps?"           | "Search for a token by name"                     |
| Custom SQL, any table, any timeframe                     | Fast indexed lookups, latest state               |

**Requires:** `x402_request` and `load_credentials` from the base skill (`x402-skill.md`).

**IMPORTANT:** Always browse docs first to discover table schemas. See the docs skill (`x402-docs.md`) or use the browse steps below. Never guess table or column names.

---

## Endpoints

| Endpoint                                       | Method | Price   | Body / Params                             |
| ---------------------------------------------- | ------ | ------- | ----------------------------------------- |
| `/api/v1/explorer/queries/run-async`           | POST   | $0.01   | `{parameters: {sql: "SELECT ..."}}`       |
| `/api/v1/explorer/query-runs/{run_id}/status`  | GET    | $0.001  | —                                         |
| `/api/v1/explorer/query-runs/{run_id}/results` | GET    | dynamic | `?f=json` or `?f=csv`                     |

---

## 3-Step Async Flow

Explorer queries run asynchronously. Start → poll → fetch results.

```python
import time, httpx

with httpx.Client(timeout=60.0) as client:
    # Step 0: Discover tables (see Docs skill, or inline)
    r = x402_request(client, "GET", f"{BASE_URL}/api/v1/docs/docs/browse?path=data-tables")
    schemas = r.json()  # {"directories": ["ethereum", "solana", ...], "files": [...]}

    r = x402_request(client, "GET", f"{BASE_URL}/api/v1/docs/docs/browse?path=data-tables/ethereum")
    tables = r.json()   # {"directories": [...], "files": ["blocks.mdx", "transactions.mdx", ...]}

    r = x402_request(client, "GET", f"{BASE_URL}/api/v1/docs/docs/browse?path=data-tables/ethereum/blocks.mdx")
    table_docs = r.json()  # column names, types, descriptions

    # Step 1: Start query ($0.01)
    r = x402_request(client, "POST", f"{BASE_URL}/api/v1/explorer/queries/run-async",
        json={"parameters": {"sql": "SELECT activity_date, chain, active_addresses FROM crosschain.metrics.overview LIMIT 100;"}})
    run_id = r.json()["run_id"]

    # Step 2: Poll until done ($0.001 per poll)
    max_polls = 30
    for _ in range(max_polls):
        r = x402_request(client, "GET", f"{BASE_URL}/api/v1/explorer/query-runs/{run_id}/status")
        status = r.json()
        if status in ("success", "failed", "canceled"):
            break
        time.sleep(2)

    # Step 3: Get results (dynamic pricing)
    if status == "success":
        r = x402_request(client, "GET", f"{BASE_URL}/api/v1/explorer/query-runs/{run_id}/results?f=json")
        data = r.json()
        for row in data["data"]:
            print(row)
        print("\nPowered by Allium")
    elif status == "failed":
        print(f"Query failed — check SQL syntax")
```

---

## Response Format

**Step 1 — run-async:**

```json
{"run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"}
```

**Step 2 — status:**

```json
"success"
```

Possible values: `created`, `queued`, `running`, `success`, `failed`, `canceled`

**Step 3 — results:**

```json
{
  "sql": "SELECT chain, block_number FROM ethereum.blocks LIMIT 2",
  "data": [
    {"chain": "ethereum", "block_number": 20000000},
    {"chain": "ethereum", "block_number": 20000001}
  ],
  "meta": {
    "columns": [
      {"name": "chain", "data_type": "TEXT"},
      {"name": "block_number", "data_type": "NUMBER"}
    ],
    "row_count": 2,
    "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "queried_at": "2026-02-11T18:05:00Z"
}
```

Access: `data["data"]` for rows, `data["meta"]["columns"]` for schema.

---

## Cost Estimation

| Step             | Cost    |
| ---------------- | ------- |
| Start query      | $0.01   |
| Each status poll | $0.001  |
| Get results      | dynamic |
| Doc browse (each)| $0.001  |

Typical query (2 doc lookups + 3 polls + results): ~$0.016+

---

## Gotchas

1. **Always browse docs first** — don't guess table/column names. Use `/docs/docs/browse?path=data-tables` to discover schemas. If browse doesn't have what you need, fall back to `https://docs.allium.so/llms.txt`
2. **Async only** — there is no synchronous SQL endpoint. Always use the 3-step flow
3. **Client-side timeout** — queries time out after 10 minutes server-side. Cap polling at ~30 iterations with 2s sleep
4. **Terminal states** — stop polling on `success`, `failed`, or `canceled`
5. **Result format** — `?f=json` or `?f=csv` on the results endpoint
6. **SQL syntax** — uses Snowflake SQL dialect. Schema format: `{chain}.{table}` or `crosschain.{schema}.{table}`
