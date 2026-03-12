# Known Differences: Dune vs Allium

Structural differences between Dune and Allium that cause **legitimate, expected** result deltas. These are not bugs — they reflect different data modeling choices.

---

## Pricing Coverage (Solana)

**Impact**: Allium `transfers_usd_value` is ~76% higher than Dune for aggregate transfer metrics.

| Aspect | Dune | Allium |
|--------|------|--------|
| Curated tokens | ~665 Coinpaprika-curated Solana tokens | Broader coverage |
| DEX-derived prices | Tokens with >$10K volume only | More tokens priced |
| Unpriced tokens | NULL `amount_usd` → contributes $0 to SUM | More tokens have prices |

### How Dune Prices Work

1. **Source**: `prices_external.hour` (Coinpaprika + DEX-derived)
2. **Join**: LEFT JOIN on `blockchain + contract_address + date_trunc('hour', block_time)`
3. **Formula**: `amount_raw / pow(10, decimals) * price`
4. **No match**: NULL `amount_usd` → $0 in aggregates

### Dune Price Pipeline Filters

| Filter | Rule |
|--------|------|
| VWMP Outlier | >3x from 7-day rolling median excluded |
| MAD Outlier | >2x median absolute deviation excluded |
| Volume bounds | Trades <$0.01 or >$1M rejected |
| Min volume | Tokens need >$10K volume for DEX-derived prices |
| Forward-fill | Hourly: 7 days, Daily: 30 days, Minute: 2 days |

### Dune Outlier Filtering

```sql
-- Applied to amount_usd in tokens_solana.transfers
CASE
    WHEN is_trusted_token = true THEN amount_usd
    WHEN is_trusted_token = false AND amount_usd < 1000000000) THEN amount_usd
    WHEN is_trusted_token = false AND amount_usd >= 1000000000) THEN NULL
END
```

### Guidance

- A ~76% delta in `transfers_usd_value` is **expected and correct**
- For exact Dune matching, you'd need to replicate their token whitelist (not practical)
- Count-based metrics (tx count, transfer count) should match closely

---

## Jupiter Aggregator Swaps

**Impact**: Row counts and per-token volumes differ significantly. Total user-level swap counts are comparable but not identical.

| Aspect | Dune (`jupiter_solana.aggregator_swaps`) | Allium (`solana.dex.aggregator_trades`) |
|--------|------|--------|
| Granularity | Individual AMM legs (N rows per multi-hop swap) | Aggregated top-level swaps (1 row per user swap) |
| AMM coverage | 61 whitelisted AMMs | 108+ fill sources |
| Missing AMMs | Silently drops legs through unlisted AMMs | Tracks all |
| Route info | Separate rows per leg | `FILL_SOURCES` array column |

### AMMs Missing from Dune's Whitelist

These AMMs are NOT in Dune's `jupiter_solana_amms.sql` (as of investigation date), causing ~1.6M legs/day to be silently dropped:

- AlphaQ
- BisonFi
- PumpSwap AMM
- Aquifer
- Manifest

### Consequences

1. **Row count**: Dune shows more rows (multiple legs) for the same user swap
2. **Per-token volume**: Intermediate routing tokens (JLP, cbBTC, USD1) appear inflated on Dune because they show up in intermediate legs
3. **Total volume**: Dune undercounts due to dropped legs through unlisted AMMs
4. **User-level metrics**: Allium is more accurate for "how many swaps did user X make"

### Guidance

- These tables are **not directly comparable** — different granularity
- For user-level swap analysis, Allium's aggregated view is simpler and more complete
- For AMM-level routing analysis, Dune's leg-level data is useful (but incomplete)
- Do not try to match Dune leg counts with Allium swap counts — they measure different things

---

## Token Transfer Amounts

| Aspect | Dune | Allium |
|--------|------|--------|
| Amount field | `amount_raw` (raw integer) — needs `/ pow(10, decimals)` | `amount` (pre-normalized, decimal-adjusted) |
| USD amount | `amount_usd` (LEFT JOIN with prices) | `usd_amount` (broader price coverage) |

### Guidance

- When converting, remove any `/ pow(10, decimals)` division — Allium `amount` is ready to use
- Watch for Dune queries that reference `amount` vs `amount_raw` — in Dune's `tokens_solana.transfers`, `amount` may already be adjusted, but `amount_raw` is not

---

## Instruction Table Structure

| Aspect | Dune | Allium |
|--------|------|--------|
| Table | Single `solana.instruction_calls` | Two tables: `solana.raw.instructions` (outer) + `solana.raw.inner_instructions` (CPI) |
| Inner instruction ID | `inner_instruction_index` column | Separate table entirely |

### Guidance

- Always UNION both Allium tables when converting queries against `solana.instruction_calls`
- If the Dune query filters `inner_instruction_index IS NULL` (outer only), use just `solana.raw.instructions`
- If the Dune query filters `inner_instruction_index IS NOT NULL` (CPI only), use just `solana.raw.inner_instructions`

---

## Transfer Type Filtering

Allium's `solana.assets.transfers` includes account closure events as transfers. Dune's `tokens_solana.transfers` does not.

| Transfer Type | Included in Dune? | Included in Allium? |
|---------------|-------------------|---------------------|
| `spl_token_transfer` | Yes | Yes |
| `sol_transfer` | Yes | Yes |
| `account_close` | No | Yes |

### Guidance

- Always filter `transfer_type IN ('spl_token_transfer', 'sol_transfer')` to match Dune behavior
- Omitting this filter inflates transfer counts and amounts on Allium

---

---

# EVM Chain Differences

## Native Token Transfers (EVM) {#native-token-transfers-evm}

**Impact**: Using Allium's `{chain}.assets.native_token_transfers` for is_value_transfer detection causes +134-456% over-counting vs Dune's `transfers_{chain}.eth` spellbook.

| Aspect | Dune (`transfers_{chain}.eth`) | Allium (`{chain}.assets.native_token_transfers`) |
|--------|------|--------|
| Scope | Curated: user-initiated ETH transfers only | Raw traces: includes gas refunds, internal contract calls, self-transfers |
| Result | Conservative count of value transfers | Inflated — nearly every tx has some native token movement |

### Guidance

- **Do NOT use `native_token_transfers` EXISTS checks** to detect "did this transaction transfer value?"
- Instead, use `t.value::DOUBLE > 0` to check for native ETH value on the transaction itself
- Combine with ERC20/ERC721/ERC1155 curated transfer tables for full value-transfer detection
- Expected delta: ~0.5-1% under-count vs Dune (Allium misses some internal ETH trace transfers that Dune's spellbook captures from traces)

## DEX Volume (EVM)

**Impact**: Allium `dex.orderflow` table captures aggregator-routed trades (Cowswap, 1inch, Bitget, BCDC, daos_world) that are not in `dex.trades`. Combining both sources gives more complete DEX coverage.

| Aspect | Dune (`dex.trades`) | Allium (`dex.trades` + `dex.orderflow`) |
|--------|------|--------|
| Aggregator trades | Included in single `dex.trades` table | Split: `dex.orderflow` for aggregators, `dex.trades` for direct DEX |
| Double-counting risk | None — single source | Must exclude orderflow txs from `dex.trades` via `TRANSACTION_HASH NOT IN (...)` |
| Column names | `tx_hash`, `amount_usd` | `TRANSACTION_HASH`, `USD_AMOUNT` (trades) / `USD_VOLUME` (orderflow) |

### Guidance

- Always combine `dex.orderflow` + `dex.trades` (minus overlapping txs) for complete DEX volume
- Column names differ from Dune: `TRANSACTION_HASH` not `tx_hash`, `USD_AMOUNT` not `amount_usd`
- Allium DEX volume may be higher or lower depending on aggregator coverage

## ERC20 Token Transfer Amounts (EVM)

**Impact**: Allium's `{chain}.assets.erc20_token_transfers.amount` is **pre-normalized** (already decimal-adjusted). Dune's `erc20_{chain}.evt_Transfer.value` is raw and needs `/ pow(10, decimals)`.

| Aspect | Dune | Allium |
|--------|------|--------|
| Amount field | `value` (raw integer, needs decimals) | `amount` (pre-normalized) |
| USD price | Requires `prices.usd` JOIN | `USD_EXCHANGE_RATE` column available directly |
| Token symbol | Requires metadata JOIN | `TOKEN_SYMBOL` column available directly |

### Guidance

- When converting, **remove** any `/ pow(10, decimals)` division — Allium `amount` is ready to use
- Allium's `USD_EXCHANGE_RATE` and `TOKEN_SYMBOL` columns can simplify queries that previously needed multiple JOINs

## Dune Community Datasets (EVM)

Several Dune queries reference community-maintained datasets that are not publicly accessible via API:

| Dataset | Content | Conversion Strategy |
|---------|---------|-------------------|
| `non_app_method_ids.non_app_method_ids` | Method selectors for non-app operations (approvals, transfers, wraps) | Inline as VALUES CTE. See [EVM_MAPPINGS.md](EVM_MAPPINGS.md#reference-data-non-app-method-signatures). |
| `labels.system_addresses` | System/infrastructure addresses per chain | Inline as VALUES CTEs. See [EVM_MAPPINGS.md](EVM_MAPPINGS.md#reference-data-system-addresses). |
| `query_XXXXX` | Materialized result sets from other saved queries | Look up query on Dune, convert and inline as CTE or Snowflake view. |

---

# Solana-Specific Differences

## Solana Balance/Holder Queries

**Impact**: Approach for historical holder analysis differs significantly between Dune and Allium.

| Aspect | Dune | Allium |
|--------|------|--------|
| Current balances | `solana_utils.latest_balances` (spellbook) | `solana.assets.spl_token_balances_latest` (fast, ~14s) |
| Historical balances | `solana_utils.daily_balances` (spellbook) | `solana.assets.spl_token_balances_daily` (**WARNING: times out on GROUP BY**) |
| Transfers-based approach | `tokens_solana.transfers` | `solana.assets.transfers` with tight date filters |

### Guidance

- For **current holder counts**: Use `solana.assets.spl_token_balances_latest` — fast and reliable
- For **historical holder tracking** (first-seen dates, cumulative counts): Use `solana.assets.transfers` with the transfers approach (sum inflows/outflows per address, HAVING balance > 0)
- **Do NOT use** `solana.assets.spl_token_balances_daily` for GROUP BY queries — it times out even with mint filters, as it's clustered by date, not mint
- Solana tables require a **large warehouse** (e.g., CHUNGUS_WH / XL). Small warehouses (X-Small) will time out on table scans
- Always add tight `block_timestamp` filters on `solana.assets.transfers` to constrain scan size

## Dune-Specific Features with No Direct Allium Equivalent

| Dune Feature | Workaround |
|--------------|------------|
| `dune.solflare.result_wallet_info` | Custom tables / parameterization |
| `http_get()` for external APIs (e.g., Jito) | Use Allium's `solana.staking.rewards` for MEV data |
| Parameterized queries (`{{param}}`) | Use Snowflake session variables or script-level substitution |
