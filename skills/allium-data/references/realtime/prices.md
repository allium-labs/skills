# Prices Reference

All commands output JSON by default. Use `--format table` for human-readable output or `--format csv` for spreadsheets.

---

### Fetch latest token price

`POST /api/v1/developer/prices`

Get the latest price for the given token addresses and chains.

#### Request

| Flag | Type | Required | Description |
| ---- | ---- | -------- | ----------- |
| `--token-address` | string | Yes | Token contract address (repeatable) |
| `--chain` | string | Yes | Lowercase chain name (repeatable) |
| `--with-liquidity-info` | boolean | No | If true, returns total_liquidity_usd as well. See this page for more details. (default: `False`) |

**Example:**

```bash
allium realtime prices latest \
  --chain ethereum \
  --token-address 0x0000000000000000000000000000000000000000
```

#### Response

| Field | Type | Always present | Description |
| ----- | ---- | -------------- | ----------- |
| `items[].timestamp` | string | Yes | ISO 8601 UTC candle time |
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].address` | string | Yes | Token contract address |
| `items[].decimals` | integer or null | No | Token decimal places |
| `items[].price` | number | Yes | Current price (USD) at the timestamp |
| `items[].open` | number | Yes | Opening price (USD) at the start of the interval |
| `items[].high` | number | Yes | Highest price (USD) during the interval |
| `items[].close` | number | Yes | Closing price (USD) at the end of the interval |
| `items[].low` | number | Yes | Lowest price (USD) during the interval |

> Access: `items[]` for the result items.

Detailed docs: `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-latest-price.md`

---

### Fetch token price history

`POST /api/v1/developer/prices/history`

Get the price history for the given token and the given time granularity.

#### Request

| Flag | Type | Required | Description |
| ---- | ---- | -------- | ----------- |
| `--cursor` | string | No | cursor |

**Example:**

```bash
allium realtime prices history \
  --chain ethereum \
  --token-address 0x0000000000000000000000000000000000000000 \
  --start-timestamp 2026-03-10T00:00:00Z \
  --end-timestamp 2026-03-17T00:00:00Z \
  --time-granularity 1h
```

#### Response

| Field | Type | Always present | Description |
| ----- | ---- | -------------- | ----------- |
| `items[].mint` | string | Yes | Token contract address |
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].decimals` | integer or null | No | Token decimal places |
| `items[].prices` | array of objects | Yes | OHLCV candle array, one entry per time interval |
| `items[].prices[].timestamp` | string | Yes | ISO 8601 UTC candle start time |
| `items[].prices[].price` | number | Yes | Volume-weighted average price (USD) over the interval |
| `items[].prices[].open` | number | Yes | Opening price (USD) at the start of the interval |
| `items[].prices[].high` | number | Yes | Highest price (USD) during the interval |
| `items[].prices[].close` | number | Yes | Closing price (USD) at the end of the interval |
| `items[].prices[].low` | number | Yes | Lowest price (USD) during the interval |

> Access: `items[]` for the result items.

Detailed docs: `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-price-history.md`

---

### Fetch token price stats

`POST /api/v1/developer/prices/stats`

Get tokens price stats like volume, high and low, price and volume change.

#### Request

| Flag | Type | Required | Description |
| ---- | ---- | -------- | ----------- |
| `--token-address` | string | Yes | Token contract address (repeatable) |
| `--chain` | string | Yes | Lowercase chain name (repeatable) |

**Example:**

```bash
allium realtime prices stats \
  --chain ethereum \
  --token-address 0x0000000000000000000000000000000000000000
```

#### Response

| Field | Type | Always present | Description |
| ----- | ---- | -------------- | ----------- |
| `items[].mint` | string | Yes | Token contract address |
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].timestamp` | string | Yes | ISO 8601 UTC timestamp |
| `items[].latest_price` | number | Yes | Latest price (USD) |
| `items[].low_24h` | number | Yes | Lowest price (USD) over last 24h |
| `items[].high_24h` | number | Yes | Highest price (USD) over last 24h |
| `items[].low_1h` | number | Yes | Lowest price (USD) over last 1h |
| `items[].high_1h` | number | Yes | Highest price (USD) over last 1h |
| `items[].percent_change_24h` | number or null | No | Price change (%) over last 24h |
| `items[].percent_change_1h` | number or null | No | Price change (%) over last 1h |
| `items[].decimals` | integer or null | No | Token decimal places |

> Access: `items[]` for the result items.

Detailed docs: `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-price-stats.md`

---

### Fetch token price at timestamp

`POST /api/v1/developer/prices/at-timestamp`

Price of a token at a given timestamp.

#### Request

| Flag | Type | Required | Description |
| ---- | ---- | -------- | ----------- |
| `--addresses` | array of objects | Yes | List of token address+chain pairs |
| `--timestamp` | string | Yes | Target timestamp (UTC ISO 8601) |
| `--time-granularity` | string | Yes | Candle granularity (15s, 1m, 5m, 1h, 1d) |
| `--staleness-tolerance` | string or null | No | Max lookback for price data (e.g. 1h, 30m) |

**Example:**

```bash
allium realtime prices at-timestamp \
  --chain ethereum \
  --token-address 0x0000000000000000000000000000000000000000 \
  --timestamp 2026-01-15T12:00:00Z \
  --time-granularity 1h
```

#### Response

| Field | Type | Always present | Description |
| ----- | ---- | -------------- | ----------- |
| `items[].input_timestamp` | string | Yes | Requested timestamp |
| `items[].price_timestamp` | string | Yes | Actual price timestamp |
| `items[].mint` | string | Yes | Token contract address |
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].price` | number | Yes | Price (USD) at the actual price timestamp |

> Access: `items[]` for the result items.

Detailed docs: `GET /api/v1/docs/docs/browse?path=api/developer/prices/token-price-at-timestamp.md`
