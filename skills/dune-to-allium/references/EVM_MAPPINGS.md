# EVM Chains: Dune → Allium Conversion Reference

Conversion mappings for EVM chains (Ethereum, Arbitrum, Base, Polygon, etc.). For SQL dialect conversions (Trino → Snowflake) that apply to all chains, see [SOLANA_MAPPINGS.md](SOLANA_MAPPINGS.md#sql-dialect-conversions-trino--snowflake).

> **Status**: This document is being built incrementally from real query conversions. Contributions welcome.

---

## Table Mappings

### Transactions

| Dune | Allium | Notes |
|------|--------|-------|
| `ethereum.transactions` | `ethereum.raw.transactions` | Validated — exact row count match |
| `optimism.transactions` | `optimism.raw.transactions` | Validated |
| `base.transactions` | `base.raw.transactions` | Validated |
| `arbitrum.transactions` | `arbitrum.raw.transactions` | Validated. Has `receipt_gas_used_for_l1` column. |
| `zora.transactions` | `zora.raw.transactions` | Validated |
| `{chain}.transactions` | `{chain}.raw.transactions` | Same pattern for all EVM chains |

### Column Mappings: Transactions

| Dune | Allium | Notes |
|------|--------|-------|
| `block_time` | `block_timestamp` | |
| `hash` | `hash` | Same |
| `from` | `from_address` | |
| `to` | `to_address` | |
| `value` | `value` | Same (raw wei) |
| `gas_used` | `receipt_gas_used` | Different name! |
| `gas_price` | `gas_price` | Same (in wei) |
| `priority_fee_per_gas` | `max_priority_fee_per_gas` | Different name! |
| `"type"` | `transaction_type` | Dune: string (`'Legacy'`, `'DynamicFee'`). Allium: integer (`0`=Legacy, `1`=AccessList, `2`=EIP-1559, `3`=Blob) |
| `success` | `receipt_status` | Allium: `1` = success, `0` = failure |
| `gas_used_for_l1` | `receipt_gas_used_for_l1` | Arbitrum only. Use `COALESCE(..., 0)` as it may be NULL. |
| `l1_fee` | `receipt_l1_fee` | OP Stack chains (Optimism, Base, Zora). Use `COALESCE(..., 0)`. |
| `effective_gas_price` | `receipt_effective_gas_price` | Arbitrum uses this for fee calculation |
| `data` | `input` | Hex string in Allium (e.g. `'0x095ea7b3...'`). Dune uses `varbinary`. |
| `block_date` | `block_timestamp` | Dune has a separate `block_date` column. In Allium, cast: `block_timestamp::DATE`. |
| `block_number` | `block_number` | Same |

### Blocks

| Dune | Allium | Notes |
|------|--------|-------|
| `ethereum.blocks` | `ethereum.raw.blocks` | |
| `{chain}.blocks` | `{chain}.raw.blocks` | Same pattern for all EVM chains |

### Column Mappings: Blocks

| Dune | Allium | Notes |
|------|--------|-------|
| `time` | `timestamp` | **Not** `block_timestamp`! |
| `number` | `number` | Same |
| `base_fee_per_gas` | `base_fee_per_gas` | Same (in wei) |
| `gas_used` | `gas_used` | Same |
| `gas_limit` | `gas_limit` | Same |

### Logs / Events

| Dune | Allium | Notes |
|------|--------|-------|
| `ethereum.logs` | `ethereum.raw.logs` | |
| `{chain}.logs` | `{chain}.raw.logs` | Same pattern for all EVM chains |

### Decoded Tables

| Dune | Allium | Notes |
|------|--------|-------|
| `{project}_{chain}.{contract}_evt_{Event}` | `{chain}.decoded.logs` | Filter by `address` + `NAME`. Extract params via `PARAMS:paramName::TYPE`. |
| `{project}_{chain}.{contract}_call_{Function}` | `{chain}.decoded.traces` | Filter by `to_address` (contract) + `NAME` (function). Extract params via `INPUT_PARAMS:paramName::TYPE` and `OUTPUT_PARAMS:paramName::TYPE`. |

#### Decoded Events: Column Mappings

| Dune (evt table) | Allium (`decoded.logs`) | Notes |
|---|---|---|
| Table per event | Single table | Filter by `address` + `NAME` |
| Event params as columns (e.g., `token0`) | `PARAMS` (VARIANT) | Extract: `PARAMS:token0::STRING` |
| `evt_tx_hash` | `transaction_hash` | |
| `evt_block_time` | `block_timestamp` | |
| `evt_block_number` | `block_number` | |
| `evt_index` | `log_index` | |
| `contract_address` | `address` | |
| N/A | `signature` | Event signature string |
| N/A | `topic0` - `topic3` | Raw log topics |

**Example: Decoded Events**

```sql
-- Dune (decoded table per contract/event)
SELECT token0, token1, fee
FROM uniswap_v3_ethereum.Factory_evt_PoolCreated
WHERE block_time >= NOW() - interval '7' day

-- Allium (unified decoded logs table)
SELECT
    block_timestamp,
    transaction_hash,
    PARAMS:token0::STRING AS token0,
    PARAMS:token1::STRING AS token1,
    PARAMS:fee::NUMBER AS fee
FROM ethereum.decoded.logs
WHERE address = '0x1F98431c8aD98523631AE4a59f267346ea31F984'  -- Uniswap V3 Factory
  AND NAME = 'PoolCreated'
  AND block_timestamp >= CURRENT_TIMESTAMP() - INTERVAL '7 days'
```

#### Decoded Calls (Traces): Column Mappings

| Dune (call table) | Allium (`decoded.traces`) | Notes |
|---|---|---|
| Table per function | Single table | Filter by `to_address` + `NAME` |
| Input params as columns (e.g., `amount`) | `INPUT_PARAMS` (VARIANT) | Extract: `INPUT_PARAMS:amount::NUMBER` |
| Output/return values as columns | `OUTPUT_PARAMS` (VARIANT) | Extract: `OUTPUT_PARAMS:returnValue::TYPE` |
| `call_tx_hash` | `transaction_hash` | |
| `call_block_time` | `block_timestamp` | |
| `call_block_number` | `block_number` | |
| `call_tx_signer` | N/A | Join with transactions for signer |
| `call_success` | `status` | `1` = success, `0` = failure |
| `contract_address` | `to_address` | The contract being called |
| N/A | `from_address` | The caller (contract or EOA) |
| N/A | `call_type` | `'call'`, `'delegatecall'`, `'staticcall'` |
| N/A | `selector` | 4-byte function selector (e.g., `'0xa9059cbb'`) |
| N/A | `trace_address` | Position in the call tree |

**Example: Decoded Calls**

```sql
-- Dune (decoded table per contract/function)
SELECT amount0, amount1, recipient
FROM uniswap_v3_ethereum.Pair_call_swap
WHERE call_success = true
  AND call_block_time >= NOW() - interval '7' day

-- Allium (unified decoded traces table)
SELECT
    INPUT_PARAMS:amount0::NUMBER AS amount0,
    INPUT_PARAMS:amount1::NUMBER AS amount1,
    INPUT_PARAMS:recipient::STRING AS recipient
FROM ethereum.decoded.traces
WHERE to_address = '0x...'  -- specific pool address
  AND NAME = 'swap'
  AND status = 1
  AND block_timestamp >= CURRENT_TIMESTAMP() - INTERVAL '7 days'
```

> **Note**: Dune consolidates all instances of a contract into one table (e.g., all Uniswap V3 pairs share `Pair_call_swap`). In Allium, you filter `to_address` for specific contracts, or omit it to get all contracts that have a function with that name. Use `interface_id` to scope to a specific ABI.

### Transfers (Curated)

| Dune | Allium | Notes |
|------|--------|-------|
| `tokens.transfers` | `{chain}.assets.transfers` | Unified transfer table |
| `erc20_{chain}.evt_Transfer` | `{chain}.assets.erc20_token_transfers` | ERC20 only. See column mappings below. |
| `nft.transfers` (ERC721) | `{chain}.assets.erc721_token_transfers` | ERC721 only. |
| `nft.transfers` (ERC1155) | `{chain}.assets.erc1155_token_transfers` | ERC1155 only. |
| `transfers_{chain}.eth` | `{chain}.assets.native_token_transfers` | **CAUTION**: Allium's table is much broader than Dune's spellbook — includes gas refunds, internal contract-to-contract calls. See [Known Differences](#native-token-transfers-evm). For simple "did this tx transfer value?", use `t.value > 0` instead. |

#### Column Mappings: ERC20 Token Transfers (`{chain}.assets.erc20_token_transfers`)

| Dune (`erc20_{chain}.evt_Transfer`) | Allium (`{chain}.assets.erc20_token_transfers`) | Notes |
|------|--------|-------|
| `contract_address` | `token_address` | Token contract address |
| `"from"` | `from_address` | |
| `"to"` | `to_address` | |
| `value` (raw, needs decimals) | `amount` | **Pre-normalized** — already decimal-adjusted. Do NOT divide by `pow(10, decimals)`. |
| N/A | `USD_EXCHANGE_RATE` | Token price at time of transfer. Allium-only — broader coverage than Dune. |
| N/A | `TOKEN_SYMBOL` | Token symbol. Allium-only convenience column. |
| `evt_tx_hash` | `transaction_hash` | |
| `evt_block_time` | `block_timestamp` | |
| `evt_block_number` | `block_number` | |

**Pattern: Mint/Burn Detection via Zero Address**

```sql
-- Mints: from zero address
SELECT * FROM ethereum.assets.erc20_token_transfers
WHERE from_address = '0x0000000000000000000000000000000000000000'
  AND token_address IN (SELECT address FROM my_tokens)

-- Burns/Redeems: to zero address
SELECT * FROM ethereum.assets.erc20_token_transfers
WHERE to_address = '0x0000000000000000000000000000000000000000'
  AND token_address IN (SELECT address FROM my_tokens)

-- Signed amount for cumulative tracking
CASE WHEN from_address = '0x0000000000000000000000000000000000000000' THEN amount
     WHEN to_address = '0x0000000000000000000000000000000000000000' THEN -amount
END AS signed_amount
```

### Raw Event Log Decoding

When decoded tables don't cover a specific event, decode directly from `{chain}.raw.logs` using topic/data byte offsets:

```sql
-- Example: Decode a custom event from raw logs
SELECT
    block_timestamp,
    transaction_hash,
    -- topic0 = event signature hash
    -- Extract fields from data using byte offsets (hex string, 2 chars per byte + '0x' prefix)
    SUBSTR(data, 2 + 128*2 + 1, 64) AS field_at_offset_128,
    TRY_TO_NUMBER(SUBSTR(data, 2 + 192*2 + 1, 64), REPEAT('X', 64)) AS numeric_field
FROM ethereum.raw.logs
WHERE topic0 = '0x...'  -- event signature
  AND address = '0x...'  -- contract address
  AND block_timestamp >= '2025-01-01'
```

**Hex math**: `data` starts with `0x`, so byte offset N starts at character position `2 + N*2 + 1`. Each 32-byte EVM word = 64 hex chars.

### Traces

| Dune | Allium | Notes |
|------|--------|-------|
| `{chain}.traces` | `{chain}.raw.traces` | Same pattern for all EVM chains |

### Prices

| Dune | Allium | Notes |
|------|--------|-------|
| `prices.usd` | `common.prices.hourly` | Cross-chain price feed. See SOLANA_MAPPINGS.md for column mapping details. |
| `prices.usd` (chain-specific) | `{chain}.prices.hourly` | Chain-specific price table. Columns: `address`, `price`, `timestamp`, `symbol`. Useful when you only need prices for one chain. |

#### Column Mappings: Chain-Specific Prices (`{chain}.prices.hourly`)

| Dune (`prices.usd`) | Allium (`{chain}.prices.hourly`) | Notes |
|------|--------|-------|
| `minute` | `timestamp` | Hourly granularity |
| `contract_address` | `address` | Token contract address |
| `price` | `price` | Same. Cast to `::FLOAT` if needed. |
| `symbol` | `symbol` | Token symbol |
| `blockchain` filter | N/A | Already chain-scoped by table name |

**Pattern: Chain-Specific Price Joins**

```sql
-- Dune
LEFT JOIN prices.usd p ON p.blockchain = 'ethereum'
  AND p.contract_address = t.token_address
  AND p.minute = date_trunc('minute', t.block_time)

-- Allium (chain-specific)
LEFT JOIN ethereum.prices.hourly p ON p.address = t.token_address
  AND p.timestamp = DATE_TRUNC('hour', t.block_timestamp)
```

### DEX Tables

| Dune | Allium | Notes |
|------|--------|-------|
| `dex.trades` | `{chain}.dex.trades` | Standard DEX trades (Uniswap, PancakeSwap, etc.). Key columns: `TRANSACTION_HASH`, `USD_AMOUNT`, `block_timestamp`. |
| N/A | `{chain}.dex.orderflow` | **Allium-only table** — aggregator-routed trades (Cowswap, 1inch, Bitget, BCDC, daos_world). Key columns: `FRONTEND`, `SWAPPER_ADDRESS`, `USER_TOKEN_INPUT`, `USER_TOKEN_OUTPUT`, `USD_VOLUME`, `TRANSACTION_HASH`, `block_timestamp`. |

#### Column Mappings: DEX Trades (`{chain}.dex.trades`)

| Column | Notes |
|--------|-------|
| `TRANSACTION_HASH` | **Not** `TX_HASH` or `tx_hash` — use exact column name |
| `USD_AMOUNT` | **Not** `AMOUNT_USD` — use exact column name |
| `block_timestamp` | Standard timestamp column |

#### DEX Query Pattern: Combining orderflow + trades

When building comprehensive DEX analytics, combine `dex.orderflow` (aggregator trades) with `dex.trades` (direct DEX trades), excluding orderflow transactions from `dex.trades` to avoid double-counting:

```sql
-- Step 1: Aggregator-routed trades (Cowswap, 1inch, etc.)
eth_orderflow AS (
    SELECT o.block_timestamp::DATE AS day, o.USD_VOLUME AS usd_amount, o.TRANSACTION_HASH
    FROM ethereum.dex.orderflow o
    WHERE o.USER_TOKEN_INPUT IN (SELECT address FROM my_tokens)
       OR o.USER_TOKEN_OUTPUT IN (SELECT address FROM my_tokens)
),
-- Step 2: Direct DEX trades, excluding already-counted orderflow txs
eth_dex AS (
    SELECT d.block_timestamp::DATE AS day, d.USD_AMOUNT AS usd_amount, d.TRANSACTION_HASH
    FROM ethereum.dex.trades d
    WHERE (d.TOKEN_BOUGHT_ADDRESS IN (SELECT address FROM my_tokens)
        OR d.TOKEN_SOLD_ADDRESS IN (SELECT address FROM my_tokens))
      AND d.TRANSACTION_HASH NOT IN (SELECT TRANSACTION_HASH FROM eth_orderflow)
),
-- Step 3: UNION ALL both sources
all_dex AS (
    SELECT * FROM eth_orderflow
    UNION ALL
    SELECT * FROM eth_dex
)
```

### BSC (BNB Chain)

BSC tables follow the same schema as Ethereum but use the `bsc` prefix — **not** `bnb` or `binance`:

| Correct | Incorrect |
|---------|-----------|
| `bsc.assets.erc20_token_transfers` | ~~`bnb.assets.erc20_token_transfers`~~ |
| `bsc.dex.trades` | ~~`binance.dex.trades`~~ |
| `bsc.dex.orderflow` | ~~`bnb.dex.orderflow`~~ |
| `bsc.raw.logs` | ~~`bnb.raw.logs`~~ |
| `bsc.prices.hourly` | ~~`binance.prices.hourly`~~ |

### Staking (Ethereum-specific)

| Dune | Allium | Notes |
|------|--------|-------|
| `staking_ethereum.info` | No equivalent | Dune spellbook table with entity metadata (names, categories, Twitter handles). Must be sourced externally or built as a reference table. |
| `staking_ethereum.deposits` | TBD | |
| `staking_ethereum.withdrawals` | TBD | |

---

## Dune Spellbook Tables

Many Dune queries reference "spellbook" tables — curated/computed tables maintained by the Dune community. These have no direct Allium equivalent and must be rebuilt from raw data or equivalent Allium curated tables.

### Common Spellbook Tables (EVM)

| Dune Spellbook Table | Allium Equivalent | Notes |
|---------------------|-------------------|-------|
| `dex.trades` | `{chain}.dex.trades` | Allium has its own DEX trades table |
| `tokens.transfers` | `{chain}.assets.transfers` | |
| `tokens.erc20` | `{chain}.assets.erc20_metadata` | Token metadata |
| `prices.usd` | `common.prices.hourly` | |
| `staking_ethereum.*` | Partial coverage | Entity metadata not available |
| `query_XXXXX` | No equivalent | Must inline or reconstruct. See note below. |

### Handling `query_XXXXX` References

Dune allows queries to reference other saved queries as tables (e.g., `FROM query_2393816`). These are materialized result sets.

**Conversion strategy:**

1. **Find the source query** — Look up the query ID on Dune to get the SQL
2. **Assess feasibility** — Can the upstream query be converted to Allium?
3. **If yes**: Convert and inline as a CTE, or create as a Snowflake view
4. **If no**: Document what Dune-specific tables it depends on (spellbook, entity labels, etc.)

---

## EVM-Specific Function Conversions

These are in addition to the general Trino → Snowflake conversions in [SOLANA_MAPPINGS.md](SOLANA_MAPPINGS.md#sql-dialect-conversions-trino--snowflake).

| Dune (Trino) | Allium (Snowflake) | Notes |
|---|---|---|
| `bytearray_substring(t.data, 1, 4)` | `SUBSTR(t.input, 1, 10)` | Dune uses varbinary (4 bytes). Allium uses hex string: `'0x'` prefix + 8 hex chars = 10 chars total. Always wrap in `LOWER()` for case-insensitive matching. |
| `bytearray_length(t.data)` | `LENGTH(t.input) / 2 - 1` | Dune counts raw bytes. Allium hex string has `0x` prefix, so `(LENGTH - 2) / 2` = byte count. |
| `0xABC...` (address literal) | `'0xabc...'` (quoted lowercase string) | Dune treats hex as varbinary. Allium stores addresses as lowercase strings. Always use `LOWER()` or lowercase literals. |

---

## Reference Data: Non-App Method Signatures

Used by the L2 Benchmarks dashboard to classify "app actions" vs simple token operations. Source: Dune `non_app_method_ids.non_app_method_ids` community dataset (not publicly accessible — values extracted from query comments).

```sql
non_app_signatures AS (
    SELECT sign FROM (VALUES
        ('0x095ea7b3'),  -- ERC20 approve
        ('0xa9059cbb'),  -- ERC20 transfer
        ('0xd0e30db0'),  -- WETH deposit (wrap)
        ('0x2e1a7d4d'),  -- WETH withdraw (unwrap)
        ('0xa22cb465'),  -- setApprovalForAll (ERC721/ERC1155)
        ('0x42842e0e'),  -- ERC721 safeTransferFrom(address,address,uint256)
        ('0x23b872dd'),  -- transferFrom (ERC20/ERC721)
        ('0xb88d4fde'),  -- ERC721 safeTransferFrom(address,address,uint256,bytes)
        ('0xf3993d11'),  -- ERC721 related
        ('0xf242432a'),  -- ERC1155 safeTransferFrom
        ('0x2eb2c2d6'),  -- ERC1155 safeBatchTransferFrom
        ('0xbede39b5'),  -- OP gas price oracle
        ('0xbf1fe420'),  -- OP gas price oracle
        ('0x6bf6a42d')   -- Arbitrum L1 info oracle
    ) AS t(sign)
)
```

Match against transactions: `LEFT JOIN non_app_signatures nas ON nas.sign = LOWER(SUBSTR(t.input, 1, 10))`

---

## Reference Data: System Addresses

Used by the L2 Benchmarks dashboard to exclude system/infrastructure transactions. Source: Dune `labels.system_addresses` (not publicly accessible — addresses identified from on-chain data).

### OP Stack System Addresses (Optimism, Base, Zora)

```sql
op_system_addresses AS (
    SELECT LOWER(address) AS address FROM (VALUES
        ('0x4200000000000000000000000000000000000015'),  -- L1Block
        ('0x4200000000000000000000000000000000000042'),  -- CrossL2Inbox / ProtocolVersions
        ('0x4200000000000000000000000000000000000006'),  -- WETH predeploy
        ('0x4200000000000000000000000000000000000007'),  -- L2CrossDomainMessenger
        ('0x4200000000000000000000000000000000000010'),  -- L2StandardBridge
        ('0x4200000000000000000000000000000000000021'),  -- L1BlockNumber
        ('0x4200000000000000000000000000000000000016'),  -- L2ToL1MessagePasser
        ('0x4200000000000000000000000000000000000011'),  -- SequencerFeeVault
        ('0x4200000000000000000000000000000000000019'),  -- BaseFeeVault
        ('0x4200000000000000000000000000000000000012'),  -- GasPriceOracle
        ('0xdeaddeaddeaddeaddeaddeaddeaddeaddead0001')   -- L1 attributes depositor
    ) AS t(address)
)
```

### Arbitrum System Addresses

```sql
arb_system_addresses AS (
    SELECT LOWER(address) AS address FROM (VALUES
        ('0x00000000000000000000000000000000000a4b05'),  -- ArbOS / L1 info
        ('0x000000000000000000000000000000000000006e'),  -- ArbAggregator
        ('0x0000000000000000000000000000000000000066'),  -- ArbRetryableTx
        ('0x0000000000000000000000000000000000000064'),  -- ArbSys
        ('0x00000000000000000000000000000000000000c8'),  -- NodeInterface
        ('0x000000000000000000000000000000000000006c'),  -- ArbInfo
        ('0x00000000000000000000000000000000000000ff')   -- ArbDebug
    ) AS t(address)
)
```

Filter: `WHERE t.to_address NOT IN (SELECT address FROM {chain}_system_addresses)`

---

## Common Conversion Patterns

### is_app_action (L2 Benchmarks)

Classifies transactions as "app actions" (meaningful application interactions) vs simple operations:

```sql
CASE
    WHEN nas.sign IS NOT NULL THEN 0                           -- non-app method signature
    WHEN t.input = '0x' AND t.receipt_gas_used = 21000 THEN 0  -- simple ETH transfer
    WHEN t.from_address = t.to_address THEN 0                   -- self-transaction
    WHEN t.receipt_status = 0 THEN 0                            -- failed transaction
    ELSE 1
END AS is_app_action
```

For Arbitrum, adjust the simple transfer check (L1 gas overhead): `receipt_gas_used - COALESCE(receipt_gas_used_for_l1, 0) <= 21000 * 1.1`

### is_value_transfer (L2 Benchmarks)

Detects whether a transaction involved a value transfer (ETH or tokens):

```sql
CASE
    WHEN t.value::DOUBLE > 0 THEN 1  -- native ETH value
    WHEN EXISTS (SELECT 1 FROM {chain}.assets.erc20_token_transfers et
        WHERE et.transaction_hash = t.hash AND et.block_number = t.block_number
          AND et.block_timestamp >= '{start}' AND et.block_timestamp < '{end}') THEN 1
    WHEN EXISTS (SELECT 1 FROM {chain}.assets.erc721_token_transfers nf
        WHERE nf.transaction_hash = t.hash AND nf.block_number = t.block_number
          AND nf.block_timestamp >= '{start}' AND nf.block_timestamp < '{end}') THEN 1
    WHEN EXISTS (SELECT 1 FROM {chain}.assets.erc1155_token_transfers nf
        WHERE nf.transaction_hash = t.hash AND nf.block_number = t.block_number
          AND nf.block_timestamp >= '{start}' AND nf.block_timestamp < '{end}') THEN 1
    ELSE 0
END AS is_value_transfer
```

**Important**: Do NOT include `native_token_transfers` in EXISTS checks — it causes massive over-counting (+134-456%) because it includes gas refunds and internal contract-to-contract ETH movements. Use `t.value > 0` for native ETH instead.

**Performance**: EXISTS semi-joins against transfer tables are expensive on long date ranges. For 180+ day queries, consider XL warehouse or pre-materializing transfer hashes per day.

### L1 Batch Submission Tracking (L2 Benchmarks)

Tracks L1 gas + blob costs for each L2 chain's data submissions to Ethereum.

**OP Stack chains (Bedrock era)**: Direct `ethereum.raw.transactions` filtering by batcher/proposer addresses. No decoded tables needed.

| Chain | Role | From Address | To Address |
|-------|------|-------------|------------|
| OP Mainnet | Tx Batch (batcher) | `0x6887246668a3b87f54deb3b94ba47a6f63f32985` | `0xff00000000000000000000000000000000000010` |
| OP Mainnet | State Batch (proposer) | `0x473300df21d047806a082244b417f96b32f13a33` | `0xdfe97868233d1aa22e815a266982f2cf17685a27` (output oracle) or `0xe5965ab5962edc7477c8520243a95517cd252fa9` (dispute game) |
| Base | Tx Batch | `0x5050f69a9786f081509234f1a7f4684b5e5b76c9` | `0xff00000000000000000000000000000000008453` |
| Base | State Batch | `0x642229f238fb9de03374be34b0ed8d9de80752c5` | `0x56315b90c40730925ec5485cf004d835058518a0` or `0x43edb88c4b80fdd2adff2412a7bebf9df42cb40e` |
| Zora | Tx Batch | `0x625726c858dbf78c0125436c943bf4b4be9d9033` | `0x6f54ca6f6ede96662024ffd61bfd18f3f4e34dff` |
| Zora | State Batch | `0x48247032092e7b0ecf5def611ad89eaf3fc888dd` | `0x9e6204f750cd866b299594e2ac9ea824e2e5f95c` |

**Arbitrum**: Uses `ethereum.decoded.logs` to find SequencerBatchDelivered events, then joins to `ethereum.raw.transactions` for gas data.

```sql
SELECT DISTINCT transaction_hash, block_number
FROM ethereum.decoded.logs
WHERE LOWER(address) = '0x1c479675ad559dc151f6ec7ed3fbf8cee79582b6'  -- SequencerInbox
  AND NAME = 'SequencerBatchDelivered'
```

**Blob cost calculation** (replaces Dune's `query_3521656` dependency):
```sql
-- Total L1 cost per batch tx = calldata gas cost + blob gas cost
receipt_gas_used::DOUBLE * gas_price::DOUBLE / 1e18
    + COALESCE(receipt_blob_gas_used::DOUBLE * receipt_blob_gas_price::DOUBLE, 0) / 1e18

-- Number of blobs per tx (each blob = 131072 blob gas)
COALESCE(receipt_blob_gas_used / 131072, 0) AS num_blobs
```

Columns used from `ethereum.raw.transactions`: `receipt_blob_gas_used`, `receipt_blob_gas_price`, `blob_versioned_hashes` (may be null), `max_fee_per_blob_gas`.

---

## Validated Conversions

### Weekly Ethereum Transaction Count (Query #6685497)

**Dune SQL:**
```sql
WITH data AS (
    SELECT date_trunc('week', block_time) AS time,
           CAST(COUNT(*) AS double) AS tx_count
    FROM ethereum.transactions
    WHERE block_time < date_trunc('week', NOW())
    GROUP BY 1
)
SELECT time, tx_count,
       AVG(tx_count) OVER (ORDER BY time ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) AS tx_count_moving_average
FROM data
```

**Allium SQL:**
```sql
WITH data AS (
    SELECT DATE_TRUNC('week', block_timestamp) AS time,
           COUNT(*)::DOUBLE AS tx_count
    FROM ethereum.raw.transactions
    WHERE block_timestamp < DATE_TRUNC('week', CURRENT_TIMESTAMP())
    GROUP BY 1
)
SELECT time, tx_count,
       AVG(tx_count) OVER (ORDER BY time ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) AS tx_count_moving_average
FROM data
```

**Changes applied:**
- `ethereum.transactions` → `ethereum.raw.transactions`
- `block_time` → `block_timestamp`
- `NOW()` → `CURRENT_TIMESTAMP()`
- `CAST(COUNT(*) AS double)` → `COUNT(*)::DOUBLE`

**Validation**: 549 rows, 0% delta on all numeric columns. Exact match.

---

### Weekly Gas Fees by Transaction Type

**Dune SQL:**
```sql
SELECT date_trunc('week', t.block_time) AS time
, t."type"
, CASE WHEN t."type"='Legacy' THEN SUM(CAST(t.gas_used/1e18 AS double) * t.gas_price)
    WHEN t."type"='DynamicFee' THEN SUM(CAST(t.gas_used/1e18 AS double) * (b.base_fee_per_gas + t.priority_fee_per_gas))
    END AS fees
, CASE WHEN t."type"='Legacy' THEN SUM(CAST(t.gas_used/1e18 AS double) * t.gas_price * pu.price)
    WHEN t."type"='DynamicFee' THEN SUM(CAST(t.gas_used/1e18 AS double) * (b.base_fee_per_gas + t.priority_fee_per_gas) * pu.price)
    END AS fees_usd
FROM ethereum.transactions t
INNER JOIN ethereum.blocks b ON t.block_number = b.number
LEFT JOIN prices.usd pu ON pu.blockchain IS NULL
    AND pu.symbol='ETH'
    AND pu.minute=date_trunc('minute', t.block_time)
WHERE block_time BETWEEN date_trunc('week', NOW() - interval '4' year) AND date_trunc('week', NOW())
GROUP BY 1, 2
```

**Allium SQL:**
```sql
SELECT DATE_TRUNC('week', t.block_timestamp) AS time,
       CASE t.transaction_type WHEN 0 THEN 'Legacy' WHEN 2 THEN 'DynamicFee' END AS type,
       CASE WHEN t.transaction_type = 0
            THEN SUM(t.receipt_gas_used * t.gas_price / 1e18)
            WHEN t.transaction_type = 2
            THEN SUM(t.receipt_gas_used * (b.base_fee_per_gas + t.max_priority_fee_per_gas) / 1e18)
       END AS fees,
       CASE WHEN t.transaction_type = 0
            THEN SUM(t.receipt_gas_used * t.gas_price / 1e18 * pu.price)
            WHEN t.transaction_type = 2
            THEN SUM(t.receipt_gas_used * (b.base_fee_per_gas + t.max_priority_fee_per_gas) / 1e18 * pu.price)
       END AS fees_usd
FROM ethereum.raw.transactions t
INNER JOIN ethereum.raw.blocks b ON t.block_number = b.number
LEFT JOIN common.prices.hourly pu
    ON pu.chain = 'ethereum' AND pu.is_native = true
    AND pu.timestamp = DATE_TRUNC('hour', t.block_timestamp)
WHERE t.block_timestamp BETWEEN DATE_TRUNC('week', CURRENT_TIMESTAMP() - INTERVAL '4 years')
                            AND DATE_TRUNC('week', CURRENT_TIMESTAMP())
  AND t.transaction_type IN (0, 2)
GROUP BY 1, t.transaction_type
ORDER BY 1, 2
```

**Changes applied:**
- `ethereum.transactions` → `ethereum.raw.transactions`
- `ethereum.blocks` → `ethereum.raw.blocks`
- `t."type"` (string: `'Legacy'`/`'DynamicFee'`) → `t.transaction_type` (integer: `0`/`2`)
- `t.gas_used` → `t.receipt_gas_used`
- `t.priority_fee_per_gas` → `t.max_priority_fee_per_gas`
- `prices.usd` (minute granularity) → `common.prices.hourly` (hourly granularity)
- `pu.blockchain IS NULL AND pu.symbol='ETH'` → `pu.chain = 'ethereum' AND pu.is_native = true`
- `pu.minute = date_trunc('minute', ...)` → `pu.timestamp = DATE_TRUNC('hour', ...)`
- `NOW()` → `CURRENT_TIMESTAMP()`
- `interval '4' year` → `INTERVAL '4 years'`
- Fee calculation: `gas_used/1e18 * gas_price` → `receipt_gas_used * gas_price / 1e18` (multiply first, then divide — avoids precision loss)
- Added `t.transaction_type IN (0, 2)` filter (Dune only returns Legacy/DynamicFee rows; Allium also has type 1=AccessList, 3=Blob)

**Gotchas discovered:**
1. **Precision**: Dune joins prices at minute granularity; Allium at hourly. This causes small USD differences.
2. **Fee calculation order**: Dune's `CAST(gas_used/1e18 AS double) * gas_price` works because Trino keeps precision. In Snowflake, `receipt_gas_used / 1e18` truncates to near-zero. Always multiply gas_used * gas_price first, then divide by 1e18.
3. **Transaction type filtering**: Dune's query implicitly only returns Legacy/DynamicFee rows. Allium includes AccessList (1) and Blob (3) types that produce NULL in the CASE, so filter them out.

**Validation**: Ran with 1-week window. DynamicFee: 3,763 ETH ($7.7M), Legacy: 219 ETH ($450K). Values are reasonable.

---

### Multi-Chain L1/L2 Gas Benchmark

**Dune SQL** (abbreviated — full query uses `{{Time Period}}` and `{{Trailing Num Periods}}` parameters):
```sql
-- Uses: optimism.transactions, base.transactions, zora.transactions,
--       arbitrum.transactions (with gas_used_for_l1), ethereum.transactions
-- Features: sequence() for date series, DATE_DIFF, CROSS JOIN UNNEST,
--           Dune parameters, multi-chain UNION ALL

SELECT DATE_TRUNC('{{Time Period}}', block_time) AS dt,
       'Arbitrum' AS chain,
       SUM(gas_used - gas_used_for_l1) AS gas_used,  -- Arbitrum subtracts L1 gas
       ...
FROM arbitrum.transactions
WHERE block_time > (SELECT dtmin FROM date_min)
GROUP BY 1, 2
```

**Allium SQL** (with parameters hardcoded to day/90):
```sql
WITH insert_end AS (
    SELECT MAX(block_timestamp) AS mbt
    FROM optimism.raw.transactions
    WHERE block_timestamp > CURRENT_TIMESTAMP() - INTERVAL '1 day'
),
date_min AS (
    SELECT
        DATE_TRUNC('day', mbt) - INTERVAL '90 days' - INTERVAL '90 days' AS dtmin,
        DATE_TRUNC('day', mbt) - INTERVAL '90 days' AS dtmin_chart,
        mbt,
        86400.0 AS num_secs_per_period
    FROM insert_end
)
SELECT *, ...moving averages...
FROM (
    SELECT DATE_TRUNC('day', block_timestamp) AS dt, 'OP Mainnet' AS chain,
           SUM(receipt_gas_used) AS gas_used,
           SUM(receipt_gas_used)::DOUBLE / (SELECT num_secs_per_period FROM date_min) AS gas_used_per_second
    FROM optimism.raw.transactions
    WHERE block_timestamp > (SELECT dtmin FROM date_min)
    GROUP BY 1, 2

    UNION ALL
    -- base.raw.transactions, zora.raw.transactions, ethereum.raw.transactions (same pattern)

    UNION ALL
    SELECT DATE_TRUNC('day', block_timestamp) AS dt, 'Arbitrum' AS chain,
           SUM(receipt_gas_used - COALESCE(receipt_gas_used_for_l1, 0)) AS gas_used,
           SUM(receipt_gas_used - COALESCE(receipt_gas_used_for_l1, 0))::DOUBLE / (SELECT num_secs_per_period FROM date_min) AS gas_used_per_second
    FROM arbitrum.raw.transactions
    WHERE block_timestamp > (SELECT dtmin FROM date_min)
    GROUP BY 1, 2
) a
WHERE dt < DATE_TRUNC('day', (SELECT mbt FROM insert_end))
  AND dt >= (SELECT dtmin_chart FROM date_min)
```

**Changes applied:**
- All `{chain}.transactions` → `{chain}.raw.transactions` (optimism, base, zora, arbitrum, ethereum)
- `block_time` → `block_timestamp`
- `gas_used` → `receipt_gas_used`
- `gas_used_for_l1` → `receipt_gas_used_for_l1` (Arbitrum only, wrapped in `COALESCE(..., 0)`)
- `NOW()` → `CURRENT_TIMESTAMP()`
- `interval '1' day` → `INTERVAL '1 day'`, `interval '90' day` → `INTERVAL '90 days'`
- `cast(... as double)` → `...::DOUBLE`
- `DATE_DIFF('second', ...)` → `DATEDIFF('second', ...)` (not needed here — hardcoded to 86400)
- `sequence() + CROSS JOIN UNNEST` → dropped (the `gs` CTE was unused in the original query)
- Dune parameters `{{Time Period}}`, `{{Trailing Num Periods}}`, `{{Show Today}}` → hardcoded values

**New patterns documented:**
- `sequence(start, end, interval)` → `TABLE(GENERATOR(ROWCOUNT => N))` with `DATEADD` (added to SOLANA_MAPPINGS.md)
- `DATE_DIFF()` → `DATEDIFF()` (added to SOLANA_MAPPINGS.md)
- Arbitrum `gas_used_for_l1` → `receipt_gas_used_for_l1`
- Multi-chain table pattern: `{chain}.transactions` → `{chain}.raw.transactions` confirmed for optimism, base, zora, arbitrum

**Validation**: 450 rows (90 days x 5 chains). All chains returned data. Gas/sec values: Base ~30M, OP ~9M, Arbitrum ~6.5M, Ethereum ~1.9M, Zora ~30K.

---

### Multi-Chain L2 Benchmarks (Dune Query #1064888) — Phases 1-3

**Scope**: 4 L2 chains (OP Mainnet, Base, Zora, Arbitrum), 90-day rolling window, daily aggregation. Powers the [L2 Benchmarks dashboard](https://dune.com/msilb7/l2-benchmarks) visualizations for tx counts, addresses, fees, gas, app actions, and value transfers.

**Dune dependencies converted**:
- `non_app_method_ids.non_app_method_ids` → inlined CTE with 14 method selectors (see Reference Data above)
- `labels.system_addresses` → inlined CTEs for OP Stack (11 addresses) and Arbitrum (7 addresses)
- `erc20_{chain}.evt_Transfer` → `{chain}.assets.erc20_token_transfers` EXISTS semi-join
- `nft.transfers` → `{chain}.assets.erc721_token_transfers` + `{chain}.assets.erc1155_token_transfers` EXISTS semi-joins
- `transfers_{chain}.eth` → `t.value::DOUBLE > 0` (NOT `native_token_transfers` — see Known Differences)
- `prices.usd` → `common.prices.hourly` with `chain = 'ethereum'` and `address = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'` (WETH)

**Key conversions applied**:
- `bytearray_substring(t.data, 1, 4)` → `LOWER(SUBSTR(t.input, 1, 10))`
- `t.data = 0x` → `t.input = '0x'`
- `t."from"` / `t."to"` → `t.from_address` / `t.to_address`
- `t.success` → `t.receipt_status` (1 = success, 0 = failure)
- Fee formulas: OP Stack `(COALESCE(receipt_l1_fee, 0) + receipt_gas_used * gas_price) / 1e18`, Arbitrum `(receipt_effective_gas_price * receipt_gas_used) / 1e18`
- `SELECT *` with JOIN → `SELECT l2.*, p.price` (avoids ambiguous column errors on shared column names like `dt`)

**Validation results**:
- **Phase 1** (core metrics): 360 rows (90 days x 4 chains). Reasonable values.
- **Phase 2** (+ is_app_action): 27 overlapping date pairs vs Dune. Avg delta 0.00-0.01% on all metrics (num_txs, transacting_addresses, fees, app_actions).
- **Phase 3** (+ is_value_transfer): Single-day test (OP Mainnet 2025-12-01). Delta: -0.70% on app_actions_value_tfer count, -0.32% on addresses. Under-count expected — Allium misses some internal ETH trace transfers that Dune's spellbook captures.

**Phase 4** (L1 costs/margins): Validated on 2-day window. L1 batch costs computed from `ethereum.raw.transactions` (OP Stack) and `ethereum.decoded.logs` SequencerBatchDelivered events (Arbitrum). Blob costs from `receipt_blob_gas_used * receipt_blob_gas_price / 1e18`. OVM 1.0/2.0 legacy events available in Allium but excluded (outside 90-day window). Margins: OP ~95%, Base ~97%, Arbitrum ~98%, Zora ~70-81%.

**Files**: `allium_l2_benchmarks_phase1.sql`, `allium_l2_benchmarks_phase2.sql`, `allium_l2_benchmarks_phase3.sql`

---

### Ondo Global Markets Dashboard (13 Dune Queries → Allium)

**Scope**: Full dashboard conversion — TVL, daily TVL, mint/redeem, DEX trades/volume, holder counts across Ethereum, BSC, and Solana. Source: [dune.com/ondo/ondo-global-markets](https://dune.com/ondo/ondo-global-markets).

**Dune queries converted**: 5581101, 5581294, 6494838, 5653710, 5583842, 5590819, 6103925, 6497143, 5584230, 6222043, 6159087, 6470878 (+ sub-query 6585668), top-level summary.

**Key table mappings discovered**:
- `erc20_{chain}.evt_Transfer` → `{chain}.assets.erc20_token_transfers` (amount pre-normalized, has `USD_EXCHANGE_RATE`)
- `prices.usd` → `{chain}.prices.hourly` (chain-specific alternative to `common.prices.hourly`)
- Dune `dex.trades` → `{chain}.dex.trades` (column: `USD_AMOUNT`, `TRANSACTION_HASH`) + `{chain}.dex.orderflow` (column: `USD_VOLUME`, `FRONTEND`)
- `solana.snapshots.token_supply` — Allium-only, used for Solana TVL (no Dune equivalent)
- `solana.assets.spl_token_balances_latest` — fast current snapshot (ADDRESS, MINT, BALANCE)

**Key patterns**:
- DEX: orderflow + dex.trades UNION ALL, excluding orderflow txs from dex.trades to avoid double-counting
- Mint/Redeem: zero-address transfers from `erc20_token_transfers`; BSC raw.logs for custom event decoding
- Holders: EVM cumulative via first-seen date from transfers; Solana via `solana.assets.transfers` (not balances tables)
- Multi-chain: 168-token lookup table as VALUES CTE, with separate address columns per chain

**Gotchas**:
- BSC chain prefix is `bsc`, not `bnb` or `binance`
- `{chain}.dex.trades` column is `TRANSACTION_HASH` (not `TX_HASH`) and `USD_AMOUNT` (not `AMOUNT_USD`)
- `solana.assets.spl_token_balances_daily` GROUP BY times out even with mint filters — use `solana.assets.transfers` instead
- Dune `http_get()` for external price APIs has no Allium equivalent — use `{chain}.prices.hourly`
- Dune query 5734802 was empty/deleted — covered by 6222043

**Validation**: TVL $569M (Dune $613M — expected delta from different price sources), DEX Vol $2.67B (Dune ~$2.23M cumulative trades), 60,813 holders (Dune ~59.7K). All within expected ranges.

**Files**: `ondo-finance/allium_*.sql` (13 files)

---

## Partially Convertible Queries

### ETH Staking Entity Dashboard (References query_2393816)

**Blocking issues:**
- Depends on `query_2393816` (Dune materialized staking deposits/withdrawals dataset)
- Uses `staking_ethereum.info` (entity metadata — no Allium equivalent)
- Uses `get_href()` (Dune UI function — no equivalent needed)

**SQL patterns identified (all chain-agnostic, documented in SOLANA_MAPPINGS.md):**
- `SUM(...) FILTER (WHERE ...)` → `SUM(CASE WHEN ... THEN ... ELSE 0 END)`
- `NOW()` → `CURRENT_TIMESTAMP()`
- `interval '7' day` → `INTERVAL '7 days'`
- `interval '1' month` → `INTERVAL '1 month'`
- `interval '6' month` → `INTERVAL '6 months'`
- `year()`, `month()`, `day()` — same in both
- `lpad()` — same in both
- `get_href()` — drop or return plain text
