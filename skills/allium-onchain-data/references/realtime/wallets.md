# Wallets API Reference

**Base URL:** `https://api.allium.so`
**Auth:** `X-API-KEY` header

---

### Fetch latest fungible token balances

`POST /api/v1/developer/wallet/balances`

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `chain` | string | Yes |  |
| `address` | string | Yes |  |
| `with_liquidity_info` | boolean | No | If true, returns total_liquidity_usd as well. See this page for more details. (default: `False`) |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/balances" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"chain": "...", "address": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/wallets/latest-token-balances.md`

---

### Fetch historical fungible token balances

`POST /api/v1/developer/wallet/balances/history`

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `start_timestamp` | string | Yes |  |
| `end_timestamp` | string | Yes |  |
| `addresses` | array of objects | Yes |  |
| `limit` | integer | No | Max number of items returned. Default is 1000. (default: `1000`) |
| `cursor` | string | No | Cursor to request the next page of results. |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/balances/history" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_timestamp": "...",
    "end_timestamp": "...",
    "addresses": [{"...": "..."}]
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/wallets/historical-token-balances.md`

---

### Fetch transactions

`POST /api/v1/developer/wallet/transactions`

Get rich transaction activity data for wallets, including activities, asset transfers, and labels.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `chain` | string | Yes |  |
| `address` | string | Yes |  |
| `activity_type` | string | No | Activity type to filter transactions by |
| `limit` | integer | No | Limit the number of transactions returned. Default is 25. (default: `25`) |
| `transaction_hash` | string | No | Filter by transaction hash |
| `cursor` | string | No | Cursor to request the next page of results. |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/transactions" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"chain": "...", "address": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/wallets/transactions.md`
