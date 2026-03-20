# Allium API Reference

**Base URL:** `https://api.allium.so`
**Rate limit:** 1/second. No batching workaround — respect it or get 429s.

---

## Supported Chains Discovery

**Call once per session** before any `/developer/` endpoint. Returns all endpoints and their chains in one response — cache it, don't re-call. Not needed for Explorer SQL or Docs endpoints.

```bash
curl "https://api.allium.so/api/v1/supported-chains/realtime-apis/simple"
```

**Response:** Map of endpoint path → array of supported chain names.

```json
{
  "/api/v1/developer/prices": ["arbitrum", "avalanche", "bsc", "base", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/balances": ["arbitrum", "base", "bitcoin", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/balances/history": ["arbitrum", "base", "bitcoin", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/transactions": ["abstract", "arbitrum", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/holdings/history": ["arbitrum", "avalanche", "base", "bitcoin", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/pnl": ["arbitrum", "avalanche", "base", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/pnl/history": ["arbitrum", "avalanche", "base", "ethereum", "solana", ...]
}
```

Use this to validate chain support before making data calls. Chain coverage varies per endpoint.

---

## Token Prices

### Current Price

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '[{"token_address": "0x...", "chain": "ethereum"}]'
```

**Response:**

```json
[
	{
		"chain": "ethereum",
		"address": "0x...",
		"price": 72154.48,
		"decimals": 8,
		"info": { "name": "Token Name", "symbol": "TKN" },
		"attributes": {
			"price_diff_1d": -3840.06,
			"price_diff_pct_1d": -5.05,
			"volume_usd_1d": 432014155.32
		}
	}
]
```

---

### Historical Prices (OHLCV)

**Different format than current price.** Don't copy-paste and change the endpoint — it will 422.

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices/history" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{
    "addresses": [{"token_address": "0x...", "chain": "ethereum"}],
    "start_timestamp": 1706572800,
    "end_timestamp": 1707177600,
    "time_granularity": "1d"
  }'
```

| Field              | Required | Notes                                     |
| ------------------ | -------- | ----------------------------------------- |
| `addresses`        | Yes      | Array of `{token_address, chain}` objects |
| `start_timestamp`  | Yes      | Unix seconds                              |
| `end_timestamp`    | Yes      | Unix seconds                              |
| `time_granularity` | Yes      | `1m`, `5m`, `15m`, `1h`, `4h`, `1d`       |

**Response:**

```json
{
	"items": [
		{
			"mint": "0x...",
			"chain": "ethereum",
			"prices": [
				{
					"timestamp": "2024-01-30T00:00:00Z",
					"open": 83977.26,
					"high": 84504.82,
					"low": 74370.21,
					"close": 83889.4,
					"price": 83925.23
				}
			]
		}
	]
}
```

---

### Price at Timestamp

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices/at-timestamp" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{"token_address": "0x...", "chain": "ethereum", "timestamp": 1706572800}'
```

---

### Price Stats

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices/stats" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '[{"token_address": "0x...", "chain": "ethereum"}]'
```

---

## Token Lookup

### Token Info by Address

```bash
curl -X POST "https://api.allium.so/api/v1/developer/tokens/chain-address" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '[{"token_address": "0x...", "chain": "ethereum"}]'
```

### List Tokens

```bash
curl -X GET "https://api.allium.so/api/v1/developer/tokens" \
  -H "X-API-KEY: $API_KEY"
```

### Token Search

Don't know the address? Search first:

```bash
curl "https://api.allium.so/api/v1/developer/tokens/search?q=bitcoin" \
  -H "X-API-KEY: $API_KEY"
```

Returns array of matches with addresses and chains.

---

## Historical Wallet Data


### Historical balances

Returns raw balance of wallet over time for every balance change in specified timeframe.

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/balances/history" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{"addresses": [{"address": "0x...", "chain": "ethereum"}], "start_timestamp": "1773259200", "end_timestamp": "1773273600"}'
```

**Response:**

```json
{
    "items": [
        {
            "chain": "solana",
            "address": "MJKqp...",
            "token": {
                "object": "token",
                "chain": "solana",
                "address": "So11111111111111111111111111111111111111112",
                "type": "sol_spl",
                "decimals": 9
            },
            "raw_balance": 855165857,
            "raw_balance_str": "855165857",
            "block_timestamp": "2025-10-07T23:49:19Z",
            "block_slot": 371892388,
            "txn_index": 1094,
            "token_account": null,
            "block_hash": "FFxtK...",
            "txn_id": "3hGkr..."
        },
        {
            "chain": "solana",
            "address": "MJKqp...",
            "token": {
                "object": "token",
                "chain": "solana",
                "address": "2FbN6ww9Z794vPFARWV5U5eQ9581hs6veNDvUzcH8AWc",
                "type": "sol_spl",
                "decimals": 6
            },
            "raw_balance": 96425095000000,
            "raw_balance_str": "96425095000000",
            "block_timestamp": "2025-10-07T23:49:14Z",
            "block_slot": 371892374,
            "txn_index": 1128,
            "token_account": "235DS...",
            "block_hash": "E4fiw...",
            "txn_id": "2yqsM..."
        },
    ]
}
```

### Historical holdings (in USD)

Returns USD Holdings of wallet over time at specified granularity time intervals.

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/holdings/history" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{"addresses": [{"address": "0x...", "chain": "ethereum"}], "start_timestamp": "1773259200", "end_timestamp": "1773273600", "granularity": "1h"}'
```

**Response:**

```json
{
    "items": [
        {
            "timestamp": "2026-03-11T23:00:00Z",
            "amount": {
                "currency": "USD",
                "amount": 1124833597.9963517
            }
        },
        {
            "timestamp": "2026-03-11T22:00:00Z",
            "amount": {
                "currency": "USD",
                "amount": 1124833600.282551
            }
        },
        {
            "timestamp": "2026-03-11T21:00:00Z",
            "amount": {
                "currency": "USD",
                "amount": 1124833601.6171582
            }
        },
        {
            "timestamp": "2026-03-11T20:00:00Z",
            "amount": {
                "currency": "USD",
                "amount": 1124833598.1187537
            }
        }
    ]
}
```

### Historical PnL

**Different format than Latest PnL.** Don't copy-paste and change the endpoint — it will 422.
Returns Profit/loss of wallet over time at specified granularity time intervals.

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/pnl/history" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{"addresses": [{"address": "3e...", "chain": "solana"}], "start_timestamp": "2026-02-10T00:00:00Z", "end_timestamp": "2026-02-11T00:00:00Z", "granularity": "1h"}'
```

| Field              | Required | Notes                                     |
| ------------------ | -------- | ----------------------------------------- |
| `addresses`        | Yes      | Array of `{address, chain}` objects       |
| `start_timestamp`  | Yes      | Unix seconds                              |
| `end_timestamp`    | Yes      | Unix seconds                              |
| `granularity`      | Yes      | `15s`, `1m`, `5m`, `1h`, `1d`             |

**Response:**

```json
{
    "items": [
        {
            "chain": "solana",
            "address": "3e...",
            "pnl": [
                {
                    "timestamp": "2025-11-04T00:00:00Z",
                    "unrealized_pnl": {
                        "currency": "USD",
                        "amount": "-4643.831342118258219999"
                    },
                    "realized_pnl": {
                        "currency": "USD",
                        "amount": "4477.313380917999945427"
                    }
                },
                {
                    "timestamp": "2025-11-05T00:00:00Z",
                    "unrealized_pnl": {
                        "currency": "USD",
                        "amount": "-5119.419867080520112712"
                    },
                    "realized_pnl": {
                        "currency": "USD",
                        "amount": "4476.494797472309850168"
                    }
                },
                {
                    "timestamp": "2025-11-06T00:00:00Z",
                    "unrealized_pnl": {
                        "currency": "USD",
                        "amount": "-5349.195516643782533032"
                    },
                    "realized_pnl": {
                        "currency": "USD",
                        "amount": "4476.170682321219571894"
                    }
                }
            ]
        }
    ]
}
```

## Latest Wallet Data

The following wallet endpoints take the same format:

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/{endpoint}" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '[{"chain": "ethereum", "address": "0xWALLET..."}]'
```

| Endpoint            | Returns                        |
| ------------------- | ------------------------------ |
| `/balances`         | Token holdings of wallet       |
| `/transactions`     | Transaction history            |
| `/pnl`              | Profit/loss of wallet          |


### Latest PnL

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/pnl" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '[{"address": "3e...", "chain": "solana"}]'
```

**Response:**

```json
{
    "items": [
        {
            "chain": "solana",
            "address": "3e...",
            "tokens": [
                {
                    "token_address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    "average_cost": {
                        "currency": "USD",
                        "amount": "0.998741156892067249"
                    },
                    "raw_balance": "488.789246",
                    "current_price": {
                        "currency": "USD",
                        "amount": "1.001312436654786531"
                    },
                    "current_balance": {
                        "currency": "USD",
                        "amount": "489.430750922915870637"
                    },
                    "realized_pnl": {
                        "currency": "USD",
                        "amount": "138.681338640813260490"
                    },
                    "unrealized_pnl": {
                        "currency": "USD",
                        "amount": "1.256813896474616383"
                    },
                    "unrealized_pnl_ratio_change": 0.00257452068033395,
                    "attributes": {
                        "total_liquidity_usd": {
                            "details": "LIQUIDITY_TOO_HIGH"
                        }
                    }
                },
                {
                    "token_address": "2YLjY53bLtsJn3Aq2wFHdF2fUeTPqYDcbNPWJ6w9pump",
                    "average_cost": {
                        "currency": "USD",
                        "amount": "0.001000297862358017"
                    },
                    "raw_balance": "85900.15",
                    "current_price": {
                        "currency": "USD",
                        "amount": "0.001000606229732188"
                    },
                    "current_balance": {
                        "currency": "USD",
                        "amount": "85.952225224929403749"
                    },
                    "realized_pnl": {
                        "currency": "USD",
                        "amount": "0E-18"
                    },
                    "unrealized_pnl": {
                        "currency": "USD",
                        "amount": "0.026488803696411861"
                    },
                    "unrealized_pnl_ratio_change": 0.0003082755504888085,
                    "attributes": {
                        "total_liquidity_usd": {
                            "amount": 2001212.5853097588
                        }
                    }
                }
            ],
            "total_balance": {
                "currency": "USD",
                "amount": "575.382976148"
            },
            "total_realized_pnl": {
                "currency": "USD",
                "amount": "138.681338640813260490"
            },
            "total_unrealized_pnl": {
                "currency": "USD",
                "amount": "1.28330270017"
            },
            "total_unrealized_pnl_ratio_change": 0.0022253819
        }
    ]
}
```

---

## Explorer API (SQL)

For custom analytics. Uses `query_id` from registration — not just `api_key`.

### Create Query (Existing Users Without query_id)

Existing API key holders need to create a query first to get a `query_id`:

```bash
curl -X POST "https://api.allium.so/api/v1/explorer/queries" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{
    "title": "Custom SQL Query",
    "config": {
      "sql": "{{ sql_query }}",
      "limit": 10000
    }
  }'
# Returns: {"query_id": "..."}
# Store it — needed for all run-async calls.
```

`{{ sql_query }}` is a placeholder substituted at runtime via `parameters.sql_query`.

---

### Start Query

```bash
curl -X POST "https://api.allium.so/api/v1/explorer/queries/${QUERY_ID}/run-async" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{"parameters": {"sql_query": "SELECT * FROM ethereum.raw.blocks LIMIT 10"}}'
# Returns: {"run_id": "..."}
```

### Poll for Results

Queries are async. Poll until `status: success`:

```bash
# Check status
curl "https://api.allium.so/api/v1/explorer/query-runs/${RUN_ID}/status" \
  -H "X-API-KEY: $API_KEY"

# Get results (only when status=success)
curl "https://api.allium.so/api/v1/explorer/query-runs/${RUN_ID}/results?f=json" \
  -H "X-API-KEY: $API_KEY"
```

**Status progression:** `created` → `queued` → `running` → `success` | `failed`

### Browse Schema

Don't guess table names:

```bash
# List databases
curl "https://api.allium.so/api/v1/docs/schemas/browse?path=" -H "X-API-KEY: $API_KEY"

# List tables
curl "https://api.allium.so/api/v1/docs/schemas/browse?path=ethereum.raw" -H "X-API-KEY: $API_KEY"

# Semantic search for table names
curl "https://api.allium.so/api/v1/docs/schemas/search?q=nft+transfers" -H "X-API-KEY: $API_KEY"
```

---

## Errors

| Status | Meaning           | Fix                                             |
| ------ | ----------------- | ----------------------------------------------- |
| 400    | Bad request       | Check JSON syntax                               |
| 401    | Unauthorized      | Check API key                                   |
| 422    | Validation failed | **Check request format** — common with /history |
| 429    | Rate limited      | Wait 1 second                                   |
| 500    | Server error      | Retry with backoff                              |

---

## Documentation & Schema Discovery

Three endpoints for finding docs and table schemas. Use these before guessing.

| Endpoint                      | Method | Purpose                                |
| ----------------------------- | ------ | -------------------------------------- |
| `/api/v1/docs/docs/browse`    | GET    | Browse doc hierarchy like a filesystem |
| `/api/v1/docs/schemas/browse` | GET    | Browse databases → schemas → tables    |
| `/api/v1/docs/schemas/search` | GET    | Semantic search for table names        |

### Browse Docs

```bash
# List root directories
curl "https://api.allium.so/api/v1/docs/docs/browse?path=" -H "X-API-KEY: $API_KEY"

# List files in a directory
curl "https://api.allium.so/api/v1/docs/docs/browse?path=api/developer" -H "X-API-KEY: $API_KEY"

# Get file content (truncated to 5000 chars)
curl "https://api.allium.so/api/v1/docs/docs/browse?path=api/overview.mdx" -H "X-API-KEY: $API_KEY"
```

### Browse Schemas

Don't guess table names — browse them:

```bash
# List all databases
curl "https://api.allium.so/api/v1/docs/schemas/browse?path=" -H "X-API-KEY: $API_KEY"

# List tables in a schema
curl "https://api.allium.so/api/v1/docs/schemas/browse?path=ethereum.raw" -H "X-API-KEY: $API_KEY"

# Get full table details (columns, types)
curl "https://api.allium.so/api/v1/docs/schemas/browse?path=ethereum.raw.blocks" -H "X-API-KEY: $API_KEY"
```

### Search Schemas

Find tables by meaning, not exact name:

```bash
curl "https://api.allium.so/api/v1/docs/schemas/search?q=DEX+trades+swaps" -H "X-API-KEY: $API_KEY"
```

Returns table name matches. Feed these into Browse Schemas for column details.
