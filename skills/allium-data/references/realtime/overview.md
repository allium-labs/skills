# Realtime API Overview

**Read this first** before calling any realtime endpoint.

---

## Supported Chains Discovery

**Call once per session** to check which chains each command supports. Cache the result — don't re-call.

```bash
allium realtime supported-chains
```

**Response:** Map of endpoint path → array of supported chain names.

```json
{
  "/api/v1/developer/prices": ["arbitrum", "avalanche", "bsc", "base", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/balances": ["arbitrum", "base", "bitcoin", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/transactions": ["abstract", "arbitrum", "ethereum", "solana", ...],
  "/api/v1/developer/wallet/pnl": ["arbitrum", "avalanche", "base", "ethereum", "solana", ...]
}
```

Chain coverage varies per endpoint. Validate before calling.

---

## Errors

| Exit / Status | Meaning           | Fix                                                  |
| ------------- | ----------------- | ---------------------------------------------------- |
| 400           | Bad request       | Check flag values and types                          |
| 401           | Unauthorized      | Run `allium auth list` — check active profile        |
| 422           | Validation failed | Wrong flags or missing required flags — run `--help` |
| 429           | Rate limited      | Wait 1 second, retry                                 |
| 500           | Server error      | Retry with backoff                                   |

The CLI exits with code 1 on API errors and prints the error message.

---

## Pagination

| Command | Paginates? | How to paginate |
|---|---|---|
| `prices latest` | No | Batch via repeatable `--chain`/`--token-address` |
| `prices at-timestamp` | No | Batch via repeatable `--chain`/`--token-address` |
| `prices history` | Yes | Pass `--cursor` from previous response |
| `prices stats` | No | Batch via repeatable `--chain`/`--token-address` |
| `tokens chain-address` | No | Batch via repeatable `--chain`/`--token-address` |
| `tokens list` | No | `--limit` (max 200) |
| `tokens search` | No | `--limit` (max 200) |
| `balances latest` | No | Batch via repeatable `--chain`/`--address` |
| `balances history` | Yes | `--limit` + `--cursor` |
| `holdings history` | No | Batch via repeatable `--chain`/`--address` |
| `transactions` | Yes | `--limit` + `--cursor` |
| `pnl latest` | No | Batch via repeatable `--chain`/`--address` |
| `pnl history` | No | Batch via repeatable `--chain`/`--address` |
| `pnl-by-token latest` | No | Batch via repeatable `--chain`/`--address`/`--token-address` |
| `pnl-by-token history` | No | Batch via repeatable `--chain`/`--address`/`--token-address` |

**How to detect more pages:**

If the response JSON has a non-null `cursor` field, pass it as `--cursor` on the next call. When `cursor` is null or items returned is 0, all results have been fetched.

For `prices history`, there is no `--limit` — just keep calling with the new `--cursor` until it returns null.

---

## Conventions

These apply to all realtime responses:

- **Money amounts:** `{ "currency": "USD", "amount": "string" }` — `amount` is a string for arbitrary precision (e.g. `"138.681338640813260490"`). Never parse as float for financial calculations.
- **Timestamps:** Always ISO 8601 UTC in both requests and responses (e.g. `"2025-12-25T00:00:00Z"`). Never compute Unix timestamps manually — LLMs routinely miscalculate them.
- **Nullable fields:** Present in the response but set to `null`, sometimes omitted entirely. Always check key existence before accessing.
- **Naming:** `mint` in price history responses = `token_address` in requests = `address` in other responses. All three mean the on-chain contract address.

---

## Common Gotchas

1. **Chain names are lowercase.** `ethereum`, `base`, `solana`, `arbitrum`, `polygon`, `hyperevm`. Uppercase fails silently.
2. **Always run `--help` first.** Each subcommand has different flags. Don't guess — `allium realtime prices history --help` shows exactly what's needed.
3. **Batch calls are free.** Multiple `--chain`/`--token-address` pairs in one call cost the same as a single pair. Always batch when possible.
4. **Don't use `--format table` as an agent.** Output gets truncated. Use the default JSON format.
5. **Pagination varies.** Some commands paginate with `--cursor`, most don't. Check the table above.
6. **422 = wrong format.** The most common error. Different commands take different flags — `prices latest` uses `--chain`/`--token-address`, but `prices history` also needs `--start-timestamp`/`--end-timestamp`/`--time-granularity`.
