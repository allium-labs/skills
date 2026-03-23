# Realtime API Overview

**Base URL:** `https://api.allium.so`
**Auth:** `X-API-KEY` header
**Rate limit:** 1/second. Exceed it → 429.

---

## Supported Chains Discovery

**Call once per session** before any `/developer/` endpoint. Returns all endpoints and their chains in one response — cache it, don't re-call.

```bash
curl "https://api.allium.so/api/v1/supported-chains/realtime-apis/simple"
```

**Response:** Map of endpoint path → array of supported chain names.

```json
{
  "/api/v1/developer/prices": ["arbitrum", "avalanche", "bsc", "base", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/balances": ["arbitrum", "base", "bitcoin", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/transactions": ["abstract", "arbitrum", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/pnl": ["bitcoin", "ethereum", "solana"]
}
```

Use this to validate chain support before making data calls. Chain coverage varies per endpoint — e.g. `pnl` only supports 3 chains while `transactions` supports 20+.

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

## Common Gotchas

- **Chain names are lowercase.** `ethereum`, `base`, `solana`, `arbitrum`, `polygon`, `hyperevm`. Uppercase fails silently.
- **Different endpoints have different body formats.** `/prices` takes an array of `{token_address, chain}`. `/prices/history` takes an object with `addresses`, `start_timestamp`, `end_timestamp`, `time_granularity`. Don't copy-paste between them — it will 422.
- **Timestamps are Unix seconds** for most endpoints (not milliseconds). Hyperliquid endpoints use milliseconds.
- **Pagination:** Most list/history endpoints support `cursor` for pagination. Check the endpoint reference for specifics.
