# Explorer (SQL Analytics)

Use Explorer when the user needs **historical analysis, cross-chain comparisons, or custom aggregations** — anything that requires SQL.

---

## Discovery

Before writing SQL, discover what catalogs / tables / docs the active profile can see. The CLI exposes four commands for this:

```bash
allium explorer schemas browse                  # list catalogs you can access
allium explorer schemas browse ethereum         # list schemas in ethereum
allium explorer schemas browse ethereum.raw     # list tables in ethereum.raw
allium explorer schemas browse ethereum.raw.blocks  # full table details (markdown)

allium explorer schemas search "DEX trades"     # semantic search across tables
                                                # → returns table IDs; feed into `schemas browse <id>`

allium explorer docs browse                     # list root of the markdown docs tree
allium explorer docs browse api/overview.mdx    # get a specific doc page
allium explorer docs search "x402 setup"        # semantic search across docs
```

Results are scoped to the active profile's permissions — if your API key / x402 wallet doesn't have USAGE on a catalog, schema, or table, it won't appear. Run `allium auth list` to check the active profile.

If `allium explorer schemas --help` returns "no such command", upgrade the CLI — see `setup.md`.

> **Fallback:** if the CLI isn't installed at all, `curl -s https://docs.allium.so/llms.txt` returns a flat doc index. Discovery via the CLI is preferred — it's auth-scoped, the `llms.txt` mirror is not.

SQL uses **Snowflake dialect**. Schema format: `{chain}.{table}` or `crosschain.{schema}.{table}`.

---

## Auth Requirements

| Command                    | API Key | x402 | Tempo |
| -------------------------- | ------- | ---- | ----- |
| `explorer run`             | Yes     | Yes  | Yes   |
| `explorer status`          | Yes     | Yes  | Yes   |
| `explorer results`         | Yes     | Yes  | Yes   |
| `explorer schemas browse`  | Yes     | Yes  | Yes   |
| `explorer schemas search`  | Yes     | Yes  | Yes   |
| `explorer docs browse`     | Yes     | Yes  | Yes   |
| `explorer docs search`     | Yes     | Yes  | Yes   |
| `explorer create-query`    | Yes     | No   | No    |
| `explorer run-sql`         | **No**  | Yes  | Yes   |

`run-sql` is the only Explorer command that's not API-key-callable; `create-query` is the only one that's API-key-only (it writes a saved query to your account). The two paths to actually execute SQL diverge by auth method — read the next two sections.

Check the active profile: `allium auth list`.

---

## Running SQL — pick the path that matches your auth

There are two ways to execute SQL on Allium. **Pick by your active profile**, not by what feels easier — `run-sql` will reject API-key requests outright.

### API key — create a saved query, then run it

This is the path for any caller using an Allium API key (`auth setup --method api_key`). API keys cannot send raw SQL to the warehouse, so you create a server-side saved query once and execute it as many times as you want, optionally with parameters.

**Step 1 — create a passthrough query (one-time):**

```bash
allium explorer create-query --passthrough
# → returns the new query record, including `query_id`. Save the id.
```

`--passthrough` writes a saved query whose SQL is just `{{ sql_query }}` — from then on, any SQL runs by passing it as a `sql_query` parameter. One create call covers every ad-hoc query for the lifetime of that API key.

**Step 2 — run any SQL:**

```bash
allium explorer run <QUERY_ID> \
  --param sql_query="SELECT block_number, block_timestamp FROM ethereum.raw.blocks ORDER BY block_number DESC LIMIT 10"
```

The CLI handles the async poll loop. Output is JSON by default.

**Pre-defined queries with typed parameters** — drop `--passthrough` and pass the SQL as an argument with Jinja `{{ name }}` placeholders:

```bash
allium explorer create-query \
  "SELECT block_number, block_timestamp FROM ethereum.raw.blocks ORDER BY block_number DESC LIMIT {{ limit }}" \
  --title "Recent ethereum blocks"

allium explorer run <QUERY_ID> --param limit=100
```

You can also pass a `.sql` file path instead of inline SQL.

**Other run flags:** `--limit N`, `--compute-profile large`, `--no-wait` (prints `run_id` and exits — poll later with `allium explorer status <RUN_ID>` and `allium explorer results <RUN_ID>`).

You can also create / edit queries in the UI at [app.allium.so](https://app.allium.so) — same `query_id` works.

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
| `explorer schemas browse` | $0.01                                                |
| `explorer schemas search` | $0.01                                                |
| `explorer docs browse`    | $0.01                                                |
| `explorer docs search`    | $0.01                                                |
| `explorer create-query`   | free (API-key only)                                  |

---

## Gotchas

1. **Always discover schemas first** — `allium explorer schemas search "..."` then `allium explorer schemas browse <id>` for column metadata. Don't guess table names.
2. **API key holders cannot use `run-sql`** — create a saved query first (`allium explorer create-query --passthrough`), then pass any SQL via `allium explorer run <QUERY_ID> --param sql_query="..."`. For pre-defined queries with typed parameters, drop `--passthrough` and pass the SQL as an argument with `{{ name }}` placeholders.
3. **Snowflake SQL dialect** — `{chain}.{table}` or `crosschain.{schema}.{table}`
4. **Server-side timeout** — queries time out after 10 minutes
5. **Result format** — `--format json` (default), `table`, or `csv`
