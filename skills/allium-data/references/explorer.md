# Explorer (SQL Analytics)

Use Explorer when the user needs **historical analysis, cross-chain comparisons, or custom aggregations** — anything that requires SQL.

---

## Discovery

Before writing SQL, discover what tables / docs are available. The released CLI exposes `run-sql`, `run`, `status`, and `results`; it does not expose `explorer schemas` or `explorer docs` commands. Use Allium's docs mirror for table discovery:

```bash
# Quick index — grep it for the table you need
curl -s https://docs.allium.so/llms.txt | grep -i "erc20"

# If the quick index doesn't include the page, search the full docs mirror
curl -s https://docs.allium.so/llms-full.txt | grep -i "ethereum/assets/token-transfers"

# Per-table page: columns, types, description
curl -s "https://docs.allium.so/historical-data/supported-blockchains/evm/ethereum/assets/token-transfers/erc20-transfers.md"
```

The quick `llms.txt` index may be truncated; use `llms-full.txt` when discovery misses a table. Copy exact docs URLs / source paths from the index or mirror instead of deriving paths by hand.

The docs mirror is **not** auth-scoped — it lists documented tables, not only the ones your profile can query. If a query later fails with a permissions error, your API key / x402 wallet lacks USAGE on that catalog; check the active profile with `allium auth list`.

SQL uses **Snowflake dialect**. Schema format: `{chain}.{table}` or `crosschain.{schema}.{table}`.

---

## Auth Requirements

| Command                    | API Key | x402 | Tempo |
| -------------------------- | ------- | ---- | ----- |
| `explorer run`             | Yes     | Yes  | Yes   |
| `explorer status`          | Yes     | Yes  | Yes   |
| `explorer results`         | Yes     | Yes  | Yes   |
| `explorer run-sql`         | **No**  | Yes  | Yes   |

`run-sql` is the only Explorer execution command that's not API-key-callable; it rejects API keys with `400: This endpoint requires machine payment authentication with a preset query ID`. The two paths to execute SQL diverge by auth method — read the next two sections.

Check the active profile: `allium auth list`.

---

## Running SQL — pick the path that matches your auth

There are two ways to execute SQL on Allium. **Pick by your active profile**, not by what feels easier — `run-sql` will reject API-key requests outright.

### API key — create a saved query, then run it

This is the path for any caller using an Allium API key (`auth setup --method api_key`). API keys cannot send raw SQL to the warehouse, so you create a server-side saved query once and execute it as many times as you want, optionally with parameters.

**Step 1 — create a passthrough query (one-time):**

The CLI has no `create-query` subcommand, so create the saved query once via the REST API:

```bash
curl -s -X POST "https://api.allium.so/api/v1/explorer/queries" \
  -H "X-API-KEY: $ALLIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"agent-passthrough","config":{"sql":"{{ sql_query }}","limit":1000,"parameters":{"sql_query":"SELECT 1"}}}'
# → {"query_id":"..."}   — save the id.
```

The saved query's SQL is just `{{ sql_query }}` — from then on, any SQL runs by passing it as a `sql_query` parameter. One create call covers every ad-hoc query for the lifetime of that API key.

**Step 2 — run any SQL:**

```bash
allium explorer run <QUERY_ID> \
  --param sql_query="SELECT block_number, block_timestamp FROM ethereum.raw.blocks ORDER BY block_number DESC LIMIT 10"
```

The CLI handles the async poll loop. Output is JSON by default.

**Pre-defined queries with typed parameters** — POST `config.sql` with Jinja `{{ name }}` placeholders instead of the `{{ sql_query }}` passthrough, then run with `--param`:

```bash
curl -s -X POST "https://api.allium.so/api/v1/explorer/queries" \
  -H "X-API-KEY: $ALLIUM_API_KEY" -H "Content-Type: application/json" \
  -d '{"title":"Recent ethereum blocks","config":{"sql":"SELECT block_number, block_timestamp FROM ethereum.raw.blocks ORDER BY block_number DESC LIMIT {{ limit }}","parameters":{"limit":100}}}'
# → {"query_id":"..."}

allium explorer run <QUERY_ID> --param limit=100
```

You can also create / edit queries in the UI at [app.allium.so](https://app.allium.so) — the same `query_id` works with `allium explorer run`.

**Other run flags:** `--limit N`, `--compute-profile large`, `--no-wait` (prints `run_id` and exits — poll later with `allium explorer status <RUN_ID>` and `allium explorer results <RUN_ID>`).

### x402 / Tempo — ad-hoc SQL directly

If your active profile is `x402_key`, `x402_privy`, or `tempo`, you can send raw SQL straight to the warehouse — `allium` handles payment, the async poll loop, and result fetching in one call.

```bash
allium explorer run-sql "SELECT block_number, block_timestamp FROM ethereum.raw.blocks ORDER BY block_number DESC LIMIT 10"
allium explorer run-sql query.sql                                # from a file
echo "SELECT COUNT(*) FROM ethereum.raw.blocks" | allium explorer run-sql -   # from stdin
allium explorer run-sql --limit 100 "SELECT * FROM ethereum.raw.blocks"
allium explorer run-sql --no-wait "SELECT * FROM ethereum.raw.blocks LIMIT 1000"
# → prints run_id; poll later with `allium explorer status <RUN_ID>` and `allium explorer results <RUN_ID>`.
```

Don't use `--format table` as an agent — output truncates.

If you try `run-sql` while on an api_key profile, the CLI fails fast with a usage error pointing back at the saved-query path above.

---

## Response Format

Results default to JSON:

```json
{
  "sql": "SELECT chain, block_number FROM ethereum.raw.blocks LIMIT 2",
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
  "queried_at": "2026-03-17T18:05:00Z"
}
```

Access: `data` for rows, `meta.columns` for schema.

---

## Query Status Values

| Status     | Meaning              |
| ---------- | -------------------- |
| `created`  | Queued               |
| `running`  | Executing            |
| `success`  | Results ready        |
| `failed`   | SQL error or timeout |
| `canceled` | Manually stopped     |

---

## Costs

| Command              | Cost per call                                        |
| -------------------- | ---------------------------------------------------- |
| `explorer run-sql`        | $0.01                                                |
| `explorer run`            | $0.01                                                |
| `explorer status`         | $0.01                                                |
| `explorer results`        | ~$0.15/min of execution time (varies with complexity) |

---

## Gotchas

1. **Discover tables from the docs mirror first** — `curl -s https://docs.allium.so/llms.txt` for the quick index, `llms-full.txt` if the quick index is truncated, then the per-table `.md` page for column metadata. The CLI has no `schemas` browser. Don't guess table names or derive docs paths by hand.
2. **API key holders cannot use `run-sql`** — create a passthrough saved query once via `POST https://api.allium.so/api/v1/explorer/queries` (the CLI has no `create-query`), then pass any SQL via `allium explorer run <QUERY_ID> --param sql_query="..."`.
3. **Snowflake SQL dialect** — `{chain}.{table}` or `crosschain.{schema}.{table}`
4. **Server-side timeout** — queries time out after 10 minutes
5. **Result format** — `--format json` (default), `table`, or `csv`
