---
name: allium-x402-docs
description: >-
  Browse Allium API documentation and blockchain table schemas.
  Use to discover available tables, columns, and endpoint details before querying.
---

# Allium Docs Browser

Use this skill to **discover what's available** before making queries. Browse API documentation, find table schemas, and understand column types.

**When to use:** Before writing SQL (Explorer), when unsure which endpoint to use (Developer), or when the user asks "what data is available?"

**Requires:** `x402_request` and `load_credentials` from the base skill (`x402-skill.md`).

---

## Endpoint

| Endpoint                     | Method | Price  | Params                          |
| ---------------------------- | ------ | ------ | ------------------------------- |
| `/api/v1/docs/docs/browse`   | GET    | $0.001 | `?path=` (directory or file)    |

Rate limit: 5/s (higher than data endpoints).

---

## Browsing Pattern

Navigate the doc tree: start broad, drill into chain, then table.

```bash
# Root — list top-level sections
curl "https://agents.allium.so/api/v1/docs/docs/browse?path="

# List a section
curl "https://agents.allium.so/api/v1/docs/docs/browse?path=api/developer"

# List chain tables
curl "https://agents.allium.so/api/v1/docs/docs/browse?path=data-tables/ethereum"

# Read a specific table schema (5000 char limit)
curl "https://agents.allium.so/api/v1/docs/docs/browse?path=data-tables/ethereum/blocks.mdx"

# API endpoint docs
curl "https://agents.allium.so/api/v1/docs/docs/browse?path=api/overview.mdx"
```

---

## Response Format

**Directory listing:**

```json
{
  "directories": ["ethereum", "solana", "base", "arbitrum"],
  "files": ["overview.mdx"]
}
```

**File content:** Returns rendered documentation text (max 5000 characters).

---

## Common Paths

| Path                              | Contents                              |
| --------------------------------- | ------------------------------------- |
| `data-tables`                     | All chain schemas                     |
| `data-tables/{chain}`             | Tables for a specific chain           |
| `data-tables/{chain}/{table}.mdx` | Column names, types, descriptions     |
| `data-tables/crosschain`          | Cross-chain aggregate tables          |
| `api/developer`                   | Developer API endpoint docs           |
| `api/overview.mdx`               | API overview and authentication       |

---

## Example: Discover Schema Before SQL

```python
with httpx.Client(timeout=60.0) as client:
    # What chains have tables?
    r = x402_request(client, "GET", f"{BASE_URL}/api/v1/docs/docs/browse?path=data-tables")
    chains = r.json()["directories"]

    # What tables does Ethereum have?
    r = x402_request(client, "GET", f"{BASE_URL}/api/v1/docs/docs/browse?path=data-tables/ethereum")
    tables = r.json()["files"]  # ["blocks.mdx", "transactions.mdx", ...]

    # What columns does the blocks table have?
    r = x402_request(client, "GET", f"{BASE_URL}/api/v1/docs/docs/browse?path=data-tables/ethereum/blocks.mdx")
    schema_docs = r.json()  # column names, types, descriptions

    print(f"Chains: {chains}")
    print(f"Ethereum tables: {tables}")
    print(f"Blocks schema: {schema_docs}")
```

---

## Fallback: llms.txt

If the `/docs/docs/browse` endpoint doesn't return what you need (empty results, missing schemas, or the path doesn't exist), fetch the full documentation index:

```bash
curl -s "https://docs.allium.so/llms.txt"
```

This returns a complete listing of all Allium documentation pages with URLs. Use it to:

- **Find the correct path** when `/docs/docs/browse` returns empty or unexpected results
- **Discover new schemas/endpoints** not yet indexed in the browse API
- **Get direct URLs** to read specific documentation pages

Always try the `/docs/docs/browse` endpoint first (it's cheaper and faster). Only fall back to `llms.txt` when browse doesn't have what you need.

---

## Gotchas

1. **Always browse before SQL** — never guess table or column names
2. **5000 char limit** — file content is truncated. For large docs, focus on the section you need
3. **Path format** — no leading slash, no trailing slash. Use `data-tables/ethereum`, not `/data-tables/ethereum/`
4. **Free-ish** — $0.001 per call, so browsing 5 pages costs $0.005. Don't hesitate to explore
5. **Fallback** — if browse doesn't have it, check `https://docs.allium.so/llms.txt` for a full doc index
