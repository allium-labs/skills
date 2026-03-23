# Tokens API Reference

**Base URL:** `https://api.allium.so`
**Auth:** `X-API-KEY` header

---

### List tokens

`GET /api/v1/developer/tokens`

List tokens, optionally sorted by a field.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `chain` | string | No | The chain of the tokens. Do not pass anything to search across all tokens. |
| `sort` | string | No | Sort by a certain field. One of: volume, trade_count, fully_diluted_valuation, address, name (default: `volume`) |
| `granularity` | string or null | No | Granularity of the sorting field. Only used if sort is volume or trade_count. |
| `order` | string | No | Sorting order. One of: asc, desc (default: `desc`) |
| `limit` | integer | No | Maximum number of tokens to return. (default: `200`) |
| `volume_usd_1d_threshold` | number | No | Minimum 1d volume in USD. Only returns tokens with volume >= this value. |
| `volume_usd_1h_threshold` | number | No | Minimum 1h volume in USD. Only returns tokens with volume >= this value. |

```bash
curl -X GET "https://api.allium.so/api/v1/developer/tokens" \
  -H "X-API-KEY: $API_KEY"
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/tokens/list-tokens.md`

---

### Fetch tokens by keyword

`GET /api/v1/developer/tokens/search`

Search tokens with a query string.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `q` | string | Yes | The query string to search in name and symbol. Performs a case-insensitive substring search. |
| `chain` | string | No | The chain of the tokens. Do not pass anything to search across all tokens. |
| `sort` | string | No | Sort by a certain field. One of: volume, trade_count, fully_diluted_valuation, address, name (default: `volume`) |
| `granularity` | string or null | No | Granularity of the sorting field. Only used if sort is volume or trade_count. |
| `order` | string | No | Sorting order. One of: asc, desc (default: `desc`) |
| `limit` | integer | No | Maximum number of tokens to return. (default: `200`) |
| `volume_usd_1d_threshold` | number | No | Minimum 1d volume in USD. Only returns tokens with volume >= this value. |
| `volume_usd_1h_threshold` | number | No | Minimum 1h volume in USD. Only returns tokens with volume >= this value. |

```bash
curl -X GET "https://api.allium.so/api/v1/developer/tokens/search?q=..." \
  -H "X-API-KEY: $API_KEY"
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/tokens/search-tokens.md`

---

### Fetch token by address

`POST /api/v1/developer/tokens/chain-address`

Get token details for the given token addresses and chains.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `token_address` | string | Yes |  |
| `chain` | string | Yes |  |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/tokens/chain-address" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"token_address": "...", "chain": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/tokens/get-tokens-by-chain-address.md`
