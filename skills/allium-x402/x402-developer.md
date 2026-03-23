---
name: allium-x402-developer
description: >-
  Realtime blockchain data: token prices, wallet balances, transactions,
  PnL, and token search via the allium CLI.
refetch_after: 30d
---

# Allium Realtime APIs

Use `allium realtime` when the user needs **current or recent** data — live prices, wallet snapshots, token lookups. Fast, indexed, up-to-date.

**When to use Realtime vs Explorer:**

| Realtime (this skill)                     | Explorer (x402-explorer.md)                        |
| ----------------------------------------- | -------------------------------------------------- |
| "What's ETH worth right now?"             | "How did ETH perform over the last year?"           |
| "Show my wallet balances"                 | "What's the total value locked across all chains?"  |
| "Get the price of SOL 2 hours ago"        | "Find the top 10 wallets by volume last month"      |
| "List all tokens on Base"                 | "Compare daily active addresses across L2s"         |
| "What's my PnL on this wallet?"           | "Custom SQL on any table"                           |
| Fast, indexed, latest state               | Analytical, aggregated, historical                  |

---

## Response Conventions

These apply to all `allium realtime` commands:

- **Wrapper:** Most endpoints return `{ "items": [...] }`. Exception: Token endpoints return a raw array `[{...}]`.
- **Money amounts:** `{ "currency": "USD", "amount": "string" }` — `amount` is a string for arbitrary precision. Never parse as float for financial calculations.
- **Timestamps:** Responses use ISO 8601 UTC (`"2026-03-17T12:00:00Z"`). Request flags accept ISO 8601 strings (e.g. `--start-timestamp 2026-03-10T00:00:00Z`).
- **Nullable fields:** Present in the response but set to `null`, sometimes omitted. Not safe to access without key-existence checks.
- **Naming:** `mint` in price history = `token_address` in requests = `address` in other responses. All three mean the on-chain contract address.

---

## Commands

### Prices

**Latest price:**

```bash
allium realtime prices latest \
  --chain ethereum --token-address 0x0000000000000000000000000000000000000000 \
  --chain base --token-address 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
```

Multiple `--chain`/`--token-address` pairs in one call for batching.

**Response:**

```json
{
  "items": [{
    "timestamp": "2026-03-17T12:00:00Z",
    "chain": "ethereum",
    "address": "0x0000000000000000000000000000000000000000",
    "decimals": 18,
    "price": 1946.49,
    "open": 1943.28,
    "high": 1946.49,
    "low": 1942.69,
    "close": 1946.49,
    "volume_24h": 0.0,
    "volume_1h": 0.0,
    "trade_count_24h": 0,
    "trade_count_1h": 0
  }]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].address` | string | Yes | Token contract address |
| `items[].price` | number | Yes | Current USD price |
| `items[].decimals` | integer | Yes | Token decimal places |
| `items[].open` | number | Yes | Opening price (latest candle) |
| `items[].high` | number | Yes | Highest price (latest candle) |
| `items[].low` | number | Yes | Lowest price (latest candle) |
| `items[].close` | number | Yes | Closing price (latest candle) |
| `items[].timestamp` | string | Yes | ISO 8601 UTC candle time |
| `items[].trade_1h` | number | Yes | Trading count in the last 1 hour |
| `items[].trade_24h` | number | Yes | Trading count in the last 24 hours |
| `items[].volume_1h` | number | Yes | Trading volume (USD) in the last 1 hour |
| `items[].volume_24h` | number | Yes | Trading volume (USD) in the last 24 hours |

> **Access:** `items[0].price`

> **Pagination:** This endpoint does not paginate. Send multiple tokens in the request array for batching.

---

**Price at a specific time:**

```bash
allium realtime prices at-timestamp \
  --chain ethereum --token-address 0x0000000000000000000000000000000000000000 \
  --timestamp 2026-01-15T12:00:00Z \
  --time-granularity 1h
```

Granularity options: `15s`, `1m`, `5m`, `1h`, `1d`.

**Response:**

```json
{
  "items": [
    {
      "input_timestamp": "2026-01-15T12:00:00Z",
      "price_timestamp": "2026-01-15T12:00:00",
      "mint": "0x0000000000000000000000000000000000000000",
      "chain": "ethereum",
      "price": 3316.032251088623
    }
  ]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].mint` | string | Yes | Token contract address (= `token_address` in request) |
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].price` | number | Yes | USD price at requested time |
| `items[].price_timestamp` | string | Yes | ISO 8601 UTC time |
| `items[].input_timestamp` | string | Yes | ISO 8601 UTC time |

> **Pagination:** This endpoint does not paginate.

---

**Price history (range):**

```bash
allium realtime prices history \
  --chain ethereum --token-address 0x0000000000000000000000000000000000000000 \
  --start-timestamp 2026-03-10T00:00:00Z \
  --end-timestamp 2026-03-10T02:00:00Z \
  --time-granularity 1h
```

**Response:**

```json
{
  "items": [{
    "mint": "0x0000000000000000000000000000000000000000",
    "chain": "ethereum",
    "decimals": 18,
    "prices": [
      {
        "timestamp": "2026-03-10T00:00:00Z",
        "price": 2009.8432502222372,
        "open": 1992.8091954321428,
        "high": 2021.8996715313835,
        "close": 2015.9781846153849,
        "low": 1965.603767263294
      },
      {
        "timestamp": "2026-03-10T01:00:00Z",
        "price": 2022.0932393856956,
        "open": 2015.350430063554,
        "high": 2023.3297004162494,
        "close": 2019.1831743979267,
        "low": 1940.9721123305908
      }
    ]
  }]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].mint` | string | Yes | Token contract address |
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].decimals` | integer | Yes | Token decimal places |
| `items[].prices` | array | Yes | OHLCV candle array, one entry per time interval |
| `items[].prices[].timestamp` | string | Yes | ISO 8601 UTC candle start time |
| `items[].prices[].open` | number | Yes | Opening price (USD) |
| `items[].prices[].high` | number | Yes | Highest price in interval (USD) |
| `items[].prices[].low` | number | Yes | Lowest price in interval (USD) |
| `items[].prices[].close` | number | Yes | Closing price (USD) |
| `items[].prices[].price` | number | Yes | Volume-weighted average price (USD) |

> **Access:** `items[0].prices` — note the **nested** `prices` array.

> **Pagination:** Use `cursor` query params. If `items` length not equals 0 or `cursor` is not None, there may be more results.

---

**24h / 1h stats:**

```bash
allium realtime prices stats \
  --chain ethereum --token-address 0x0000000000000000000000000000000000000000
```

Returns high, low, volume, trade count, and percent change.

**Response:**

```json
{
  "items": [
    {
      "mint": "0x0000000000000000000000000000000000000000",
      "chain": "ethereum",
      "timestamp": "2026-03-23T04:30:23",
      "low_all_time": 2050.40035998008,
      "high_all_time": 2205.610647622688,
      "latest_price": 2055.6667408286303,
      "low_24h": 804.4040243101435,
      "high_24h": 2948.897427582476,
      "low_1h": 2050.394655001495,
      "high_1h": 2205.610647622688,
      "volume_1h": 4611606.73127028,
      "volume_24h": 181635302.33545393,
      "percent_change_24h": -0.02691402814446851,
      "percent_change_1h": null,
      "decimals": 18
    }
  ]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].mint` | string | Yes | Token contract address |
| `items[].decimals` | integer | Yes | Token decimal places |
| `items[].timestamp` | string | Yes | ISO 8601 UTC candle start time |
| `items[].latest_price` | number | Yes | Latest price (USD) |
| `items[].low_all_time` | number | Yes | Lowest price (USD) all-time |
| `items[].high_all_time` | number | Yes | Highest price (USD) all-time |
| `items[].low_24h` | number | Yes | Lowest price (USD) in the last 24 hours |
| `items[].high_24h` | number | Yes | Highest price (USD) in the last 24 hours |
| `items[].low_1h` | number | Yes | Lowest price (USD) in the last 1 hour |
| `items[].high_1h` | number | Yes | Highest price (USD) in the last 1 hour |
| `items[].volume_1h` | number | Yes | Trading volume (USD) in the last 1 hour |
| `items[].volume_24h` | number | Yes | Trading volume (USD) in the last 24 hours |
| `items[].percent_change_1h` | number | Yes | Percentage change in price (USD) in the last 1 hour |
| `items[].percent_change_24h` | number | Yes | Percentage change in price (USD) in the last 24 hours |

> **Access:** `items[0].volume_24h` — data is inside `items[]`.

> **Pagination:** This endpoint does not paginate. Send multiple tokens in the request array for batching.

---

### Tokens

**Search by name/ticker:**

```bash
allium realtime tokens search -q bitcoin --limit 2
```

Optional `--chain` filter.

**Response:**

```json
[
  {
    "object": "token",
    "chain": "ethereum",
    "address": "0x8236a87084f8b84306f72007f36f2618a5634494",
    "price": 68288.43633227484,
    "decimals": 8,
    "info": {
      "name": "Lombard Staked Bitcoin",
      "symbol": "LBTC"
    },
    "attributes": {
      "price_diff_1d": -871.563987725167,
      "price_diff_pct_1d": -1.2602139729503792,
      "price_diff_1h": -51.552977088766056,
      "price_diff_pct_1h": -0.07543603329434896,
      "total_supply": 11003.78016058,
      "fully_diluted_valuation_usd": 751430940.9101163,
      "volume_usd_1h": 65931.87000000001,
      "volume_usd_1d": 1570398.1804147102,
      "trade_count_1h": 3,
      "trade_count_1d": 59,
      "all_time_high": 125409.15822228948,
      "all_time_low": 54139.64614930077,
      "holders_count": 24924
    }
  },
  {
    "object": "token",
    "chain": "solana",
    "address": "Hnsq38nRxTr4CuwHUJgGSy1xguXnTexJ36L7LBgcpump",
    "price": 2.2078678375777897e-06,
    "decimals": 6,
    "info": {
      "name": "Instead of buying bitcoin",
      "symbol": "Me in 2010"
    },
    "attributes": {
      "total_supply": 999826414.149772,
      "fully_diluted_valuation_usd": 2207.484582962013,
      "volume_usd_1h": 243.99202600163,
      "volume_usd_1d": 171476.6067792907,
      "trade_count_1h": 10,
      "trade_count_1d": 5282,
      "all_time_high": 5.520762559937418e-05,
      "all_time_low": 1.8603287143577035e-06,
      "holders_count": 700
    }
  },
]
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `[].chain` | string | Yes | Lowercase chain name |
| `[].address` | string | Yes | Token contract address |
| `[].object` | string | Yes | Type of asset (always returns "token") |
| `[].price` | string | Yes | Current USD price |
| `[].info.name` | string | Yes | Human-readable token name |
| `[].info.symbol` | string | Yes | Token ticker symbol |
| `[].decimals` | integer | Yes | Token decimal places |
| `[].attributes` | object | Yes | Token metadata |
| `[].attributes.total_supply` | string | Yes | Total supply of the token |
| `[].attributes.fully_diluted_valuation_usd` | string | Yes | Total market value (USD) assuming maximum supply in circulation, at current token price |
| `[].attributes.volume_usd_1h` | string | Yes | Trading volume (USD) in the last 1 hour |
| `[].attributes.volume_usd_1d` | string | Yes | Trading volume (USD) in the last 24 hours |
| `[].attributes.trade_count_1h` | string | Yes | Trading count in the last 1 hour |
| `[].attributes.trade_count_1d` | string | Yes | Trading count in the last 24 hours |
| `[].attributes.all_time_high` | string | Yes | Highest price (USD) all-time |
| `[].attributes.all_time_low` | string | Yes | Lowest price (USD) all-time |
| `[].attributes.holders_count` | string | Yes | Number of wallets holding the token |

> **Access:** `items[0].address` — data is inside `items[]`.

> **Pagination:** This endpoint does not paginate.

---

**Lookup by chain + address:**

```bash
allium realtime tokens chain-address \
  --chain ethereum --token-address 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
```

**Response:**

```json
[
  {
    "object": "token",
    "chain": "ethereum",
    "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "price": 2069.193077954222,
    "decimals": 18,
    "info": {
      "name": "Wrapped Ether",
      "symbol": "WETH"
    },
    "attributes": {
      "price_diff_1d": -49.91819597127733,
      "price_diff_pct_1d": -2.355619385611946,
      "price_diff_1h": 18.023458294314878,
      "price_diff_pct_1h": 0.8786917533082049,
      "total_supply": 2583368.54888642,
      "fully_diluted_valuation_usd": 5345488319.160424,
      "volume_usd_1h": 8259142.933761937,
      "volume_usd_1d": 419020574.2605091,
      "trade_count_1h": 7178,
      "trade_count_1d": 193143,
      "all_time_high": 4948.308923568548,
      "all_time_low": 126.69547352352085,
      "token_creation_time": "2017-12-12T11:17:35Z",
      "holders_count": 2868761
    }
  }
]

```

| Field | Type | Always present | Description |
|---|---|---|---|
| `[].chain` | string | Yes | Lowercase chain name |
| `[].address` | string | Yes | Token contract address |
| `[].object` | string | Yes | Type of asset (always returns "token") |
| `[].price` | string | Yes | Current USD price |
| `[].info.name` | string | Yes | Human-readable token name |
| `[].info.symbol` | string | Yes | Token ticker symbol |
| `[].decimals` | integer | Yes | Token decimal places |
| `[].attributes` | object | Yes | Token metadata |
| `[].attributes.price_diff_1d` | string | Yes | Price difference 24 hours ago vs. current time |
| `[].attributes.price_diff_pct_1d` | string | Yes | Percentage of price difference 24 hours ago vs. current time |
| `[].attributes.price_diff_1h` | string | Yes |  Price difference 1 hour ago vs. current time |
| `[].attributes.price_diff_pct_1h` | string | Yes | Percentage of price difference 1 hour ago vs. current time |
| `[].attributes.total_supply` | string | Yes | Total supply of the token |
| `[].attributes.fully_diluted_valuation_usd` | string | Yes | Total market value (USD) assuming maximum supply in circulation, at current token price |
| `[].attributes.volume_usd_1h` | string | Yes | Trading volume (USD) in the last 1 hour |
| `[].attributes.volume_usd_1d` | string | Yes | Trading volume (USD) in the last 24 hours |
| `[].attributes.trade_count_1h` | string | Yes | Trading count in the last 1 hour |
| `[].attributes.trade_count_1d` | string | Yes | Trading count in the last 24 hours |
| `[].attributes.all_time_high` | string | Yes | Highest price (USD) all-time |
| `[].attributes.all_time_low` | string | Yes | Lowest price (USD) all-time |
| `[].attributes.token_creation_time` | string | Yes | ISO 8601 UTC token creation time |
| `[].attributes.holders_count` | string | Yes | Number of wallets holding the token |

> **Access:** `[0].info.symbol` - note that this endpoint does not have a top-level "items" key in the response

> **Pagination:** This endpoint does not paginate. Send multiple tokens in the request array for batching.

---

**List top tokens:**

```bash
allium realtime tokens list --chain ethereum --sort volume --order desc --limit 2
```

Sort options: `volume`, `trade_count`, `fully_diluted_valuation`, `address`, `name`.

**Response:**

```json
[
  {
    "object": "token",
    "chain": "ethereum",
    "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "price": 0.9988516547802732,
    "decimals": 6,
    "info": {
      "name": "USD Coin",
      "symbol": "USDC"
    },
    "attributes": {
      "price_diff_1d": -0.00167520577037783,
      "price_diff_pct_1d": -0.1674323635305365,
      "price_diff_1h": -0.0012029132734060477,
      "price_diff_pct_1h": -0.12028476363516595,
      "total_supply": 53091535260.239136,
      "fully_diluted_valuation_usd": 53030567849.51508,
      "volume_usd_1h": 10145631.030702338,
      "volume_usd_1d": 682524356.3382449,
      "trade_count_1h": 3603,
      "trade_count_1d": 139035,
      "all_time_high": 1.27317375791263,
      "all_time_low": 0.2906942278341328,
      "token_creation_time": "2018-08-03T19:28:24Z",
      "holders_count": 7426737
    }
  },
  {
    "object": "token",
    "chain": "ethereum",
    "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "price": 0.9979455162814825,
    "decimals": 6,
    "info": {
      "name": "Tether USD",
      "symbol": "USDT"
    },
    "attributes": {
      "price_diff_1d": -0.0017954712857607413,
      "price_diff_pct_1d": -0.1795936455631191,
      "price_diff_1h": -0.0018310169611241989,
      "price_diff_pct_1h": -0.1831426224003882,
      "total_supply": 101704292537.00153,
      "fully_diluted_valuation_usd": 101495342723.88092,
      "volume_usd_1h": 7503009.336470511,
      "volume_usd_1d": 604076883.2500367,
      "trade_count_1h": 3325,
      "trade_count_1d": 98324,
      "all_time_high": 1.3358830842128202,
      "all_time_low": 0.3253476456977439,
      "token_creation_time": "2017-11-28T00:41:21Z",
      "holders_count": 14606612
    }
  }
]
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `[].chain` | string | Yes | Lowercase chain name |
| `[].address` | string | Yes | Token contract address |
| `[].object` | string | Yes | Type of asset (always returns "token") |
| `[].price` | string | Yes | Current USD price |
| `[].info.name` | string | Yes | Human-readable token name |
| `[].info.symbol` | string | Yes | Token ticker symbol |
| `[].decimals` | integer | Yes | Token decimal places |
| `[].attributes` | object | Yes | Token metadata |
| `[].attributes.price_diff_1d` | string | Yes | Price difference 24 hours ago vs. current time |
| `[].attributes.price_diff_pct_1d` | string | Yes | Percentage of price difference 24 hours ago vs. current time |
| `[].attributes.price_diff_1h` | string | Yes |  Price difference 1 hour ago vs. current time |
| `[].attributes.price_diff_pct_1h` | string | Yes | Percentage of price difference 1 hour ago vs. current time |
| `[].attributes.total_supply` | string | Yes | Total supply of the token |
| `[].attributes.fully_diluted_valuation_usd` | string | Yes | Total market value (USD) assuming maximum supply in circulation, at current token price |
| `[].attributes.volume_usd_1h` | string | Yes | Trading volume (USD) in the last 1 hour |
| `[].attributes.volume_usd_1d` | string | Yes | Trading volume (USD) in the last 24 hours |
| `[].attributes.trade_count_1h` | string | Yes | Trading count in the last 1 hour |
| `[].attributes.trade_count_1d` | string | Yes | Trading count in the last 24 hours |
| `[].attributes.all_time_high` | string | Yes | Highest price (USD) all-time |
| `[].attributes.all_time_low` | string | Yes | Lowest price (USD) all-time |
| `[].attributes.token_creation_time` | string | Yes | ISO 8601 UTC token creation time |
| `[].attributes.holders_count` | string | Yes | Number of wallets holding the token |

> **Access:**

- `[0].price` - note that this endpoint does not have a top-level "items" key in the response

> **Pagination:** This endpoint does not paginate.

---

### Wallet Balances

**Current balances:**

```bash
allium realtime balances latest \
  --chain ethereum --address 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
```

**Response:**

```json
{
  "items": [{
      "chain": "ethereum",
      "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "token": {
        "object": "token",
        "chain": "ethereum",
        "address": "0x7cd167b101d2808cfd2c45d17b2e7ea9f46b74b6",
        "type": "evm_erc20",
        "price": 0.992132559549105,
        "decimals": 18,
        "info": {
          "name": "USD Coin",
          "symbol": "USDC"
        },
        "attributes": {}
      },
      "raw_balance": 260794140590000000000,
      "raw_balance_str": "260794140590000000000",
      "block_timestamp": "2022-01-30T14:56:11Z",
      "block_number": 14107783,
      "block_hash": "0xa513b4c41cf1ed00897a8ab9324c68efe6adb7eda04297da1b019ae369e6ea6c"
    },
    {
      "chain": "ethereum",
      "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "token": {
        "object": "token",
        "chain": "ethereum",
        "address": "0x054f76beed60ab6dbeb23502178c52d6c5debe40",
        "type": "evm_erc20",
        "price": 3.7060102835149265e-05,
        "decimals": 18,
        "info": {
          "name": "DeFiner",
          "symbol": "FIN"
        },
        "attributes": {}
      },
      "raw_balance": 16800000000000000000000,
      "raw_balance_str": "16800000000000000000000",
      "block_timestamp": "2022-01-12T21:10:45Z",
      "block_number": 13993078,
      "block_hash": "0x687e4c992c700432a0de9dba78c4b45d7b855f205347dc95b5db486c5cfddb32"
    },
  ]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].address` | string | Yes | Wallet address |
| `items[].token` | object | Yes | Token metadata |
| `items[].token.object` | string | Yes | Type of asset (always returns "token") |
| `items[].token.address` | string | Yes | Token contract address |
| `items[].token.type` | string | Yes | Token standard |
| `items[].token.decimals` | integer | Yes | Token decimal places |
| `items[].token.price` | integer | No | Current USD price |
| `items[].token.info.name` | string | No | Human-readable token name |
| `items[].token.info.symbol` | string | No | Token ticker symbol |
| `items[].raw_balance` | number | Yes | Balance in smallest unit |
| `items[].raw_balance_str` | string | Yes | Same as `raw_balance` as string (safe for large numbers) |
| `items[].block_timestamp` | string | No | ISO 8601 UTC timestamp of block containing this balance change |
| `items[].block_number` | integer | No | Block number containing this balance change |
| `items[].block_hash` | string | No | Hash of block containing this balance change |

> **Access:** `items[0].raw_balance` — one entry per token the wallet holds.

> **Pagination:** Returns all token balances for the wallet. Send multiple wallets in the request array for batching.

---

**Historical balances:**

```bash
allium realtime balances history \
  --chain ethereum --address 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  --start-timestamp 2026-03-01T00:00:00Z \
  --end-timestamp 2026-03-17T00:00:00Z \
  --limit 2
```

**Response:**

```json
{
  "items": [
    {
      "chain": "ethereum",
      "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "token": {
        "object": "token",
        "chain": "ethereum",
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "type": "evm_erc20"
      },
      "raw_balance": 150857442690,
      "raw_balance_str": "150857442690",
      "block_timestamp": "2026-03-15T10:13:23Z",
      "block_number": 24662218,
      "block_hash": "0x6f4d49d2b31b051b963a1a6b04fe759ce1345e96b050e0114bf407ed4caf240b"
    },
    {
      "chain": "ethereum",
      "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "token": {
        "object": "token",
        "chain": "ethereum",
        "address": "0x0000000000000000000000000000000000000000",
        "type": "evm_erc20"
      },
      "raw_balance": 0,
      "raw_balance_str": "0",
      "block_timestamp": "2026-03-14T22:49:59Z",
      "block_number": 24658815,
      "block_hash": "0xd1cc280d961b5a7d2a305e425be151a3ab99932972d4abac895c75ad281ab5eb"
    }
  ]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].address` | string | Yes | Wallet address |
| `items[].token` | object | Yes | Token metadata |
| `items[].token.object` | string | Yes | Type of asset (always returns "token") |
| `items[].token.chain` | string | Yes | Lowercase chain name |
| `items[].token.address` | string | Yes | Token contract address |
| `items[].token.type` | string | Yes | Type of token contract, e.g evm_erc20 |
| `items[].raw_balance` | number | Yes | Balance in smallest unit at this point |
| `items[].raw_balance_str` | string | Yes | Same as string (safe for large numbers) |
| `items[].block_timestamp` | string | No | ISO 8601 UTC timestamp of block containing this balance change |
| `items[].block_number` | integer | No | Block number containing this balance change |
| `items[].block_hash` | string | No | Hash of block containing this balance change. `null` on Solana chain and Near chain. |
| `items[].block_slot` | integer | No | Solana-specific: slot number. `null` on EVM chains and Near chain. |
| `items[].token_account` | string | No | Solana-specific: associated token account. `null` on EVM chains and Near chain. |
| `items[].txn_index` | integer | No | Solana-specific: Transaction index within the block |
| `items[].txn_id` | string | No | Solana-specific: Transaction hash/signature |
| `items[].block_height` | integer | No | Near-specific: height number. `null` on EVM chains and Solana chain. |
| `items[].account_id` | string | No | Near-specific: associated account id. `null` on EVM chains and Solana chain. |

> **Access:** `items[0].raw_balance` — each entry is a single balance change event.

> **Pagination:** Use `limit` and `cursor` query params. If `items` length not equals 0 or `cursor` is not None, there may be more results.

---

### Transactions

```bash
allium realtime transactions \
  --chain ethereum --address 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  --lookback-days 7 \
  --limit 50
```

Optional `--activity-type` filter (e.g. `dex_trade`, `transfer`). `--lookback-days` is a CLI convenience that translates to a `start_timestamp` filter on the underlying API.

**Response:**

```json
{
  "items": [
    {
      "id": "ethereum_0x50f45b892994fb142768fd9bfdd22fbca960b5332ad641b1a95e080df910bfc4_265",
      "type": 0,
      "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "chain": "ethereum",
      "hash": "0x50f45b892994fb142768fd9bfdd22fbca960b5332ad641b1a95e080df910bfc4",
      "index": 265,
      "within_block_order_key": 265,
      "block_timestamp": "2026-03-23T05:32:59Z",
      "block_number": 24718152,
      "block_hash": "0x6a4959a5db2f28405050b737bd6b1e0f98b4cd06be9930ecd0eb787751cabb33",
      "fee": {
        "raw_amount": "3684518641160",
        "amount_str": "0.00000368451864116",
        "amount": 3.68451864116e-06
      },
      "labels": [],
      "from_address": "0x974caa59e49682cda0ad2bbe82983419a2ecc400",
      "to_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "asset_transfers": [],
      "activities": []
    },
    {
      "id": "ethereum_0x6628584ecd01e4fb28a6f8b56f1a27a97319eca5ba23b651bb297c8dc9d4f968_253",
      "type": 2,
      "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "chain": "ethereum",
      "hash": "0x6628584ecd01e4fb28a6f8b56f1a27a97319eca5ba23b651bb297c8dc9d4f968",
      "index": 253,
      "within_block_order_key": 253,
      "block_timestamp": "2026-03-23T05:32:59Z",
      "block_number": 24718152,
      "block_hash": "0x6a4959a5db2f28405050b737bd6b1e0f98b4cd06be9930ecd0eb787751cabb33",
      "fee": {
        "raw_amount": "2944181655740",
        "amount_str": "0.00000294418165574",
        "amount": 2.94418165574e-06
      },
      "labels": [],
      "from_address": "0x1c60a038583af5b0e4e70610611041478e6fa2fc",
      "to_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "asset_transfers": [],
      "activities": []
    }
  ],
  "cursor": "eyJldGhlcmV1bSI6eyJibG9ja190aW1lc3RhbXAiOjE3NzQyNDM5NzkuMCwiYmxvY2tfbnVtYmVyIjoyNDcxODE1Miwid2l0aGluX2Jsb2NrX29yZGVyX2tleSI6MjUzLCJ0cmFuc2FjdGlvbl9oYXNoIjoiMHg2NjI4NTg0ZWNkMDFlNGZiMjhhNmY4YjU2ZjFhMjdhOTczMTllY2E1YmEyM2I2NTFiYjI5N2M4ZGM5ZDRmOTY4In19"
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].address` | string | Yes | Wallet address queried |
| `items[].id` | string | Yes |  |
| `items[].type` | integer | Yes | Type of transaction |
| `items[].hash` | string | Yes | Transaction hash |
| `items[].index` | string | Yes | Block Transaction index containing transaction |
| `items[].within_block_order_key` | string | Yes | Block Transaction index containing transaction |
| `items[].block_timestamp` | string | No | ISO 8601 UTC timestamp of block containing this balance change |
| `items[].block_number` | integer | No | Block number containing this balance change |
| `items[].block_hash` | string | No | Hash of block containing this balance change |
| `items[].fee` | object | Yes | Fees involved for this transaction event |
| `items[].fee.raw_amount` | number | Yes | Fees in smallest unit |
| `items[].fee.amount_str` | string | Yes | Same as raw_amount (safe for large numbers) |
| `items[].fee.amount` | number | Yes | Same as raw_amount (not safe for large numbers) |
| `items[].labels` | array | |
| `items[].from_address` | string | Yes | Sender address |
| `items[].to_address` | string | Yes | Recipient address |
| `items[].asset_transfers` | array | Yes | Sent and received transfers across 2 wallet addresses |
| `items[].asset_transfers[].transfer_type` | string | Yes | Enum of either "sent" or "received" |
| `items[].asset_transfers[].operation` | string | No | Enum of either "mint" or "burn" |
| `items[].asset_transfers[].transaction_hash` | string | Yes | Transaction hash containing transfer |
| `items[].asset_transfers[].log_index` | string | No | Log index of transfer |
| `items[].asset_transfers[].from_address` | string | Yes | Wallet address initializing the transfer |
| `items[].asset_transfers[].to_address` | string | Yes | Wallet address receiving the transfer  |
| `items[].asset_transfers[].asset` | object | Yes | Enum of either "sent" or "received" |
| `items[].asset_transfers[].amount` | object | Yes | Amount of asset transferred |
| `items[].activities` | array | Yes | Transaction activities details (e.g `"transfer"`, `"dex_trade"`) |

> **Access:** `items[0].txn_hash` — one entry per transaction.

> **Pagination:** Use `limit` and `cursor` query params. If `items` length not equals 0 or `cursor` is not None, there may be more results.

---

### Holdings

**Historical Holdings:**

```bash
allium realtime holdings history \
  --chain ethereum --address 0x... \
  --start-timestamp 2026-03-01T00:00:00Z \
  --end-timestamp 2026-03-17T00:00:00Z \
  --granularity 1d \
  --limit 100
```

Granularity options: `15s`, `1m`, `5m`, `1h`, `1d`.

**Response:**

```json
{
  "items": [{
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
  }]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].timestamp` | string | Yes | ISO 8601 UTC interval start time |
| `items[].amount` | object | Yes | Total USD value of all holdings |
| `items[].amount.currency` | string | Yes | Always `"USD"` |
| `items[].amount.amount` | number | Yes | Portfolio value in USD. Note: this is a number, not a string (unlike PnL amounts) |

> **Access:** `items[0].amount.amount` — each entry is a portfolio-wide USD snapshot at the given interval.

> **Pagination:** Returns all intervals in the requested range. Adjust `granularity` or narrow the time range to control result size.

---

### Profit & Loss

**Current PnL:**

```bash
allium realtime pnl latest \
  --chain ethereum --address 0x...
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

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].address` | string | Yes | Wallet address |
| `items[].tokens` | array | Yes | Per-token PnL breakdown |
| `items[].tokens[].token_address` | string | Yes | Token contract address |
| `items[].tokens[].average_cost` | object | Yes | Money amount — average acquisition cost per token |
| `items[].tokens[].raw_balance` | string | Yes | Token balance (human-readable, already decimal-adjusted) |
| `items[].tokens[].current_price` | object | Yes | Money amount — current token price |
| `items[].tokens[].current_balance` | object | Yes | Money amount — current USD value of holdings |
| `items[].tokens[].realized_pnl` | object | Yes | Money amount — realized PnL. `"0E-18"` means zero |
| `items[].tokens[].unrealized_pnl` | object | Yes | Money amount — unrealized PnL |
| `items[].tokens[].unrealized_pnl_ratio_change` | number | Yes | Unrealized PnL as a ratio (0.01 = 1%) |
| `items[].tokens[].attributes.total_liquidity_usd` | object | Yes | **Two shapes:** `{"amount": number}` when known, `{"details": "LIQUIDITY_TOO_HIGH"}` when pool is too large to measure |
| `items[].total_balance` | object | Yes | Money amount — total portfolio value |
| `items[].total_realized_pnl` | object | Yes | Money amount — total realized PnL |
| `items[].total_unrealized_pnl` | object | Yes | Money amount — total unrealized PnL |
| `items[].total_unrealized_pnl_ratio_change` | number | Yes | Portfolio-wide unrealized PnL ratio |

> **Access:**
- `items[0]["tokens"]` for per-token breakdown
- `items[0]["total_balance"]` for portfolio total
- `items[0]["total_unrealized_pnl"]` for total unrealized PnL

> **Pagination:** This endpoint does not paginate. Send multiple wallets in the request array for batching.

---

**Historical PnL:**

```bash
allium realtime pnl history \
  --chain ethereum --address 0x... \
  --start-timestamp 2026-03-01T00:00:00Z \
  --end-timestamp 2026-03-17T00:00:00Z \
  --granularity 1d
```

Granularity options: `15s`, `1m`, `5m`, `1h`, `1d`.

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
                }
            ]
        }
    ]
}
```

| Field | Type | Always present | Description |
|---|---|---|---|
| `items[].chain` | string | Yes | Lowercase chain name |
| `items[].address` | string | Yes | Wallet address |
| `items[].pnl` | array | Yes | Nested PnL array — one entry per time interval |
| `items[].pnl[].timestamp` | string | Yes | ISO 8601 UTC interval start time |
| `items[].pnl[].unrealized_pnl` | object | Yes | Money amount — unrealized PnL at this point |
| `items[].pnl[].unrealized_pnl.amount` | string | Yes | **String** for arbitrary precision. Can be negative. |
| `items[].pnl[].realized_pnl` | object | Yes | Money amount — realized PnL at this point |
| `items[].pnl[].realized_pnl.amount` | string | Yes | **String** for arbitrary precision. Can be negative. |

> **Access:** `items[0].pnl` — note the **nested** `pnl` array. Amounts are strings, not numbers.

> **Pagination:** Returns all intervals in the requested range. Adjust `granularity` or narrow the time range to control result size.

---

## Pagination

| Command | Paginates? | Mechanism | Max page size |
|---|---|---|
| `prices latest` | No | All results returned. Batch via multiple `--chain`/`--token-address` pairs. | N/A |
| `prices at-timestamp` | No | All results returned. Batch via multiple `--chain`/`--token-address` pairs. | N/A |
| `prices history` | Yes | Paginated via `--cursor` flag | N/A |
| `prices stats` | No | All results returned. Batch via multiple `--chain`/`--token-address` pairs. | N/A |
| `tokens chain-address` | No | All results returned. Batch via multiple `--chain`/`--token-address` pairs. | N/A |
| `tokens search` | No | All results returned | 200 |
| `tokens list` | No | All results returned | 200 |
| `balances latest` | No | All results returned | N/A |
| `balances history` | Yes | Paginated via `--limit` + `--cursor` flags | N/A |
| `holdings history` | No | All results returned. Batch via multiple `--chain`/`--token-address` pairs. | N/A |
| `transactions` | Yes | `--limit` + `--cursor` flags | N/A |
| `pnl latest` | No | All results returned. Batch via multiple `--chain`/`--token-address` pairs. | N/A |
| `pnl history` | No | All results returned. Batch via multiple `--chain`/`--token-address` pairs. | N/A |

**How to detect more results:**

1. For paginated commands, if the `cursor` field in the response is not None, there are more pages to fetch. When number of items returned is 0 or `cursor` field is None, that means we have fetched all results. Use the non-null `cursor` field in response and pass `--limit` and `--cursor` to fetch the next page.

2. For historical prices pagination, `--limit` parameter is not provided. Keep calling with the newly returned cursor until `cursor` in response is None, which means all results have been fetched.

---

## Timestamp Formats

**In request flags:** Use ISO 8601 UTC strings (e.g. `--start-timestamp 2026-03-10T00:00:00Z`).

**In responses:** Always ISO 8601 UTC format (`"2026-03-17T12:00:00Z"`).

---

## Endpoint Costs

| Command                          | Cost per call |
| -------------------------------- | ------------- |
| `realtime prices latest`         | $0.02         |
| `realtime prices at-timestamp`   | $0.02         |
| `realtime prices history`        | $0.02         |
| `realtime prices stats`          | $0.02         |
| `realtime tokens search`         | $0.03         |
| `realtime tokens chain-address`  | $0.02         |
| `realtime tokens list`           | $0.03         |
| `realtime balances latest`       | $0.01         |
| `realtime balances history`      | $0.01         |
| `realtime holdings history`      | $0.01         |
| `realtime transactions`          | $0.03         |
| `realtime pnl`                   | $0.01         |
| `realtime pnl history`           | $0.01         |

Batch calls (multiple `--chain`/`--token-address` pairs) cost the same as a single pair.

---

## JSON body override

Every command accepts `--body` to pass a raw JSON payload (inline string or path to `.json` file), overriding individual flags. Useful for complex or pre-built requests.

---

## Cost Tracking

```bash
allium mp cost           # total spend summary
allium mp cost list      # itemized payment history
```

---

## Gotchas

1. **Response access:** Always `items[0]`, never top-level array
2. **Price history:** Different structure — nested `prices` array inside each item
3. **Batch = same price:** Multiple `--chain`/`--token-address` pairs in one call cost the same as one
4. **Chain names:** Always lowercase (`ethereum`, not `Ethereum`)
5. **PnL amounts are strings:** Arbitrary precision — don't parse as float for financial math
6. **Liquidity field has two shapes:** `{"amount": number}` or `{"details": "LIQUIDITY_TOO_HIGH"}` — check which shape before accessing
7. **Holdings amounts are numbers, PnL amounts are strings:** Different precision handling between endpoints
