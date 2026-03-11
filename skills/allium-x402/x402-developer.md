---
name: allium-x402-developer
description: >-
  Realtime blockchain data: token prices, wallet balances, transactions,
  PnL, and token search. Use for current/recent data where freshness matters.
---

# Allium Developer APIs (Realtime)

Use these endpoints when the user needs **current or recent** data — live prices, wallet snapshots, token lookups. Think Postgres-style indexed queries: fast, structured, up-to-date.

**When to use Developer vs Explorer:**

| Developer (this skill)                    | Explorer (x402-explorer.md)                        |
| ----------------------------------------- | -------------------------------------------------- |
| "What's ETH worth right now?"             | "How did ETH perform over the last year?"           |
| "Show my wallet balances"                 | "What's the total value locked across all chains?"  |
| "Get the price of SOL 2 hours ago"        | "Find the top 10 wallets by volume last month"      |
| "List all tokens on Base"                 | "Compare daily active addresses across L2s"         |
| "What's my PnL on this wallet?"           | "Custom SQL on any table"                           |
| Fast, indexed, latest state               | Analytical, aggregated, historical                  |

**Requires:** `x402_request` and `load_credentials` from the base skill (`x402-skill.md`).

---

## Supported Chains

Call **once per session** before any developer endpoint. Cache the result.

```bash
curl "https://agents.allium.so/api/v1/supported-chains/realtime-apis/simple"
```

Returns `{ "/api/v1/developer/prices": ["ethereum", "solana", ...] }` — validate chain before calling.

---

## Endpoints

| Endpoint                                    | Method | Price  | Body                                                                                      |
| ------------------------------------------- | ------ | ------ | ----------------------------------------------------------------------------------------- |
| `/api/v1/developer/prices`                  | POST   | $0.002 | `[{token_address, chain}]`                                                                |
| `/api/v1/developer/prices/at-timestamp`     | POST   | $0.002 | `{addresses: [{token_address, chain}], timestamp, time_granularity}`                      |
| `/api/v1/developer/prices/history`          | POST   | $0.002 | `{addresses: [{token_address, chain}], start_timestamp, end_timestamp, time_granularity}` |
| `/api/v1/developer/prices/stats`            | POST   | $0.002 | `[{token_address, chain}]`                                                                |
| `/api/v1/developer/tokens/chain-address`    | POST   | $0.002 | `[{token_address, chain}]`                                                                |
| `/api/v1/developer/tokens`                  | GET    | $0.003 | —                                                                                         |
| `/api/v1/developer/tokens/search`           | GET    | $0.003 | `?q=bitcoin`                                                                              |
| `/api/v1/developer/wallet/balances`         | POST   | $0.003 | `[{chain, address}]`                                                                      |
| `/api/v1/developer/wallet/balances/history` | POST   | $0.003 | `{addresses: [{chain, address}], start_timestamp, end_timestamp}`                         |
| `/api/v1/developer/wallet/transactions`     | POST   | $0.003 | `[{chain, address}]`                                                                      |
| `/api/v1/developer/wallet/pnl`             | POST   | $0.003 | `[{chain, address}]`                                                                      |

---

## Response Formats

### Current Price (`/prices`)

```json
{
  "items": [{
    "timestamp": "2026-02-11T16:19:59Z",
    "chain": "ethereum",
    "address": "0x0000000000000000000000000000000000000000",
    "decimals": 18,
    "price": 1946.49,
    "open": 1943.28,
    "high": 1946.49,
    "low": 1942.69,
    "close": 1946.49
  }]
}
```

Access: `data["items"][0]["price"]` — NOT `data[0]["price"]`.

### Price History (`/prices/history`) — different structure

```json
{
  "items": [{
    "mint": "0x...",
    "chain": "ethereum",
    "prices": [{
      "timestamp": "2024-01-30T00:00:00Z",
      "open": 83977.26,
      "high": 84504.82,
      "low": 74370.21,
      "close": 83889.4,
      "price": 83925.23
    }]
  }]
}
```

Access: `data["items"][0]["prices"]` — note the nested `prices` array.

`time_granularity` options: `15s`, `1m`, `5m`, `1h`, `1d`

---

## Examples

### Current Price

```python
with httpx.Client(timeout=60.0) as client:
    r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices",
        json=[{"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"}])
    price = r.json()["items"][0]["price"]
    print(f"ETH: ${price:,.2f}")
```

### Batch Prices (multiple tokens, one call, $0.002)

```python
tokens = [
    {"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"},
    {"token_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "chain": "ethereum"},
    {"token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "chain": "base"},
]
r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices", json=tokens)
for item in r.json()["items"]:
    print(f"{item['chain']}: ${item['price']}")
```

### Wallet Balances

```python
r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/wallet/balances",
    json=[{"chain": "ethereum", "address": "0x..."}])
for item in r.json()["items"]:
    print(f"{item['token_symbol']}: {item['raw_balance']}")
```

### Price History (24h, hourly)

```python
r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices/history",
    json={
        "addresses": [{"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"}],
        "start_timestamp": "2026-02-10T00:00:00Z",
        "end_timestamp": "2026-02-11T00:00:00Z",
        "time_granularity": "1h"
    })
for point in r.json()["items"][0]["prices"]:
    print(f"{point['timestamp']}: ${point['price']:,.2f}")
```

### Token Search

```python
r = x402_request(client, "GET", f"{BASE_URL}/api/v1/developer/tokens/search?q=bitcoin")
for token in r.json()["items"]:
    print(f"{token['symbol']} on {token['chain']}: {token['address']}")
```

---

## Cost Estimation

| Use Case                      | Calls   | Cost   |
| ----------------------------- | ------- | ------ |
| Single price check            | 1       | $0.002 |
| 10-token portfolio price      | 1 batch | $0.002 |
| Wallet balance + PnL          | 2       | $0.006 |
| Hourly price monitoring (24h) | 24      | $0.048 |
| Full wallet analytics         | 4       | $0.011 |

---

## Gotchas

1. **Response access:** Always `data["items"][0]`, never `data[0]`
2. **Price history:** Different structure — nested `prices` array inside each item
3. **422 on /history:** Usually a malformed body — check `addresses` is an array of objects, timestamps are ISO 8601
4. **Batch = same price:** Sending 10 tokens in one array costs the same as 1
5. **Supported chains:** Validate before calling — not all endpoints support all chains
