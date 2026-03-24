# Holdings API Reference

**Base URL:** `https://api.allium.so`
**Auth:** `X-API-KEY` header

---

### Fetch holdings history

`POST /api/v1/developer/wallet/holdings/history`

Get historical aggregated USD holdings for an address.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `granularity` | string | Yes |  |
| `start_timestamp` | string | Yes |  |
| `end_timestamp` | string | Yes |  |
| `addresses` | array of objects | Yes |  |
| `cursor` | string | No | cursor |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/holdings/history" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "granularity": "...",
    "start_timestamp": "...",
    "end_timestamp": "...",
    "addresses": [{"...": "..."}]
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/holdings/holdings-history.md`

---

### Fetch current PnL by Wallet

`POST /api/v1/developer/wallet/pnl`

Get the PnL for a given wallet address.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `chain` | string | Yes |  |
| `address` | string | Yes |  |
| `min_liquidity` | number | No | min_liquidity (default: `10000`) |
| `min_volume_24h` | number | No | min_volume_24h (default: `10000`) |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/pnl" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"chain": "...", "address": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/holdings/holdings-pnl.md`

---

### Fetch historical PnL by Wallet

`POST /api/v1/developer/wallet/pnl/history`

Get the Historical PnL for a given wallet address.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `granularity` | string | Yes |  |
| `addresses` | array of objects | Yes |  |
| `start_timestamp` | string | Yes |  |
| `end_timestamp` | string | Yes |  |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/pnl/history" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "granularity": "...",
    "addresses": [{"...": "..."}],
    "start_timestamp": "...",
    "end_timestamp": "..."
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/holdings/holdings-pnl-history.md`

---

### Fetch current PnL by Wallet & Token

`POST /api/v1/developer/wallet/pnl-by-token`

Get the PnL for a given wallet and token address.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `chain` | string | Yes |  |
| `address` | string | Yes |  |
| `token_address` | string | Yes |  |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/pnl-by-token" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"chain": "...", "address": "...", "token_address": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/holdings/holdings-pnl-by-token.md`

---

### Fetch historical PnL by Wallet & Token

`POST /api/v1/developer/wallet/pnl-by-token/history`

Get the Historical PnL for a given wallet address and token address.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `granularity` | string | Yes |  |
| `addresses` | array of objects | Yes |  |
| `start_timestamp` | string | Yes |  |
| `end_timestamp` | string | Yes |  |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/wallet/pnl-by-token/history" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "granularity": "...",
    "addresses": [{"...": "..."}],
    "start_timestamp": "...",
    "end_timestamp": "..."
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/holdings/holdings-pnl-by-token-history.md`
