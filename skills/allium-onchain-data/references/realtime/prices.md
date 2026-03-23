# Prices API Reference

**Base URL:** `https://api.allium.so`
**Auth:** `X-API-KEY` header

---

### Fetch latest token price

`POST /api/v1/developer/prices`

Get the latest price for the given token addresses and chains.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `token_address` | string | Yes |  |
| `chain` | string | Yes |  |
| `with_liquidity_info` | boolean | No | If true, returns total_liquidity_usd as well. See this page for more details. (default: `False`) |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"token_address": "...", "chain": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-latest-price.md`

---

### Fetch token price history

`POST /api/v1/developer/prices/history`

Get the price history for the given token and the given time granularity.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `start_timestamp` | string | Yes |  |
| `end_timestamp` | string | Yes |  |
| `addresses` | array of objects | Yes |  |
| `time_granularity` | string | Yes |  |
| `cursor` | string | No | cursor |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices/history" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_timestamp": "...",
    "end_timestamp": "...",
    "addresses": [{"...": "..."}],
    "time_granularity": "..."
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-price-history.md`

---

### Fetch token price stats

`POST /api/v1/developer/prices/stats`

Get tokens price stats like volume, high and low, price and volume change.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `token_address` | string | Yes |  |
| `chain` | string | Yes |  |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices/stats" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"token_address": "...", "chain": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-price-stats.md`

---

### Fetch token price at timestamp

`POST /api/v1/developer/prices/at-timestamp`

Price of a token at a given timestamp.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `addresses` | array of objects | Yes |  |
| `timestamp` | string | Yes |  |
| `time_granularity` | string | Yes |  |
| `staleness_tolerance` | string or null | No |  |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/prices/at-timestamp" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [{"...": "..."}],
    "timestamp": "...",
    "time_granularity": "..."
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-price-at-timestamp.md`
