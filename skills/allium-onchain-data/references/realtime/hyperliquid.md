# Hyperliquid API Reference

**Base URL:** `https://api.allium.so`
**Auth:** `X-API-KEY` header

---

### Info

`POST /api/v1/developer/trading/hyperliquid/info`

Hyperliquid API without rate limits.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `type` | string | No | Request type parameter |
| `user` | string | No | User parameter |
| `dex` | string | No | DEX parameter |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/trading/hyperliquid/info" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{

  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/hyperliquid/info.md`

---

### Fills

`POST /api/v1/developer/trading/hyperliquid/info/fills`

Endpoint providing fills by user address

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `type` | string | Yes | Type of fills to retrieve. Applies to all request types. |
| `user` | string | Yes | User's wallet address (hex string). Applies to all request types. |
| `startTime` | integer | No | Start time filter (Unix timestamp in milliseconds). Required for userFillsByTime. Only applies to userFillsByTime. |
| `endTime` | integer | No | End time filter (Unix timestamp in milliseconds). Only applies to userFillsByTime. |
| `aggregateByTime` | boolean | No | When true, aggregates multiple fills from the same order at the same timestamp into a single fill with combined size,... |
| `twapMode` | string | No | Controls TWAP fill filtering: 'none' (default) excludes TWAP fills, 'include' returns both regular and TWAP fills, 'o... |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/trading/hyperliquid/info/fills" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "...",
    "user": "..."
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/hyperliquid/fills.md`

---

### Order history

`POST /api/v1/developer/trading/hyperliquid/info/order/history`

Endpoint providing order history by user address

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `type` | string | Yes | Request type - must be 'historicalOrders' |
| `user` | string | Yes | User's wallet address (hex string) |
| `startTime` | integer | No | Start time filter (Unix timestamp in milliseconds) |
| `endTime` | integer | No | End time filter (Unix timestamp in milliseconds) |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/trading/hyperliquid/info/order/history" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "...",
    "user": "..."
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/hyperliquid/order-history.md`

---

### Order status

`POST /api/v1/developer/trading/hyperliquid/info/order/status`

Endpoint providing order status by user address

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `type` | string | Yes | Request type - must be 'orderStatus' |
| `user` | string | Yes | User's wallet address (hex string) |
| `oid` | any | Yes | Order ID - can be either numeric order ID or string client order ID |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/trading/hyperliquid/info/order/status" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "...",
    "user": "...",
    "oid": "..."
  }'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/hyperliquid/order-status.md`

---

### L4 Orderbook snapshot

`GET /api/v1/developer/trading/hyperliquid/orderbook/snapshot`

Get complete orderbook snapshot for all pairs.

```bash
curl -X GET "https://api.allium.so/api/v1/developer/trading/hyperliquid/orderbook/snapshot" \
  -H "X-API-KEY: $API_KEY"
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/hyperliquid/orderbook-snapshot.md`
