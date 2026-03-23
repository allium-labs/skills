# Solana: Dune → Allium Conversion Reference

Comprehensive mapping for converting Dune (Trino) Solana queries to Allium (Snowflake).

---

## Table Mappings

### Instructions

| Dune | Allium | Notes |
|------|--------|-------|
| `solana.instruction_calls` | `solana.raw.instructions` UNION `solana.raw.inner_instructions` | Dune combines outer + inner (CPI) in one table. **Always UNION both** when converting. |

**Pattern: Combining Outer + Inner Instructions**

```sql
-- Allium equivalent of Dune's solana.instruction_calls
WITH all_instructions AS (
    SELECT block_timestamp, txn_id, program_id, accounts, data, parent_tx_success
    FROM solana.raw.instructions
    WHERE block_timestamp >= '{start}' AND block_timestamp < '{end}'
      AND parent_tx_success = true

    UNION ALL

    SELECT block_timestamp, txn_id, program_id, accounts, data, parent_tx_success
    FROM solana.raw.inner_instructions
    WHERE block_timestamp >= '{start}' AND block_timestamp < '{end}'
      AND parent_tx_success = true
)
SELECT * FROM all_instructions
WHERE program_id = '{program_address}'
```

### Transactions

| Dune | Allium | Notes |
|------|--------|-------|
| `solana.transactions` | `solana.raw.transactions` | |

### Account Activity / Transfers

| Dune | Allium | Notes |
|------|--------|-------|
| `solana.account_activity` | `solana.assets.transfers` | Dune has pre-computed `balance_change`. Allium has no equivalent. Use `transfers` with `to_address`/`from_address` filter. Do NOT use `solana.assets.balances` with LAG — it misses first events per address/mint. |
| `tokens_solana.transfers` | `solana.assets.transfers` | Allium `amount` is already decimal-adjusted. Dune `amount_raw` needs `/ pow(10, decimals)`. |
| `system_program_solana.system_program_call_Transfer` | `solana.assets.transfers` with `transfer_type = 'sol_transfer'` | Dune has decoded program-specific tables; Allium uses unified transfers table. |

### DEX / Jupiter

| Dune | Allium | Notes |
|------|--------|-------|
| `jupiter_solana.aggregator_swaps` | `solana.dex.aggregator_trades` | **Structural difference** — see KNOWN_DIFFERENCES.md. Dune = individual AMM legs (N rows per swap). Allium = aggregated top-level swaps (1 row per user swap). |

### Prices

| Dune | Allium | Notes |
|------|--------|-------|
| `prices.usd` | `common.prices.hourly` | Different filtering — see column mappings below. |

### Decoded Instructions

| Dune | Allium | Notes |
|------|--------|-------|
| Program-specific tables (e.g., `jupiter_solana.referral_call_initializeReferralTokenAccount`) | `solana.decoded.instructions` | Filter by `program_id` + `NAME`. Access fields via `PARSED_DATA:data:field_name::TYPE`. |

### Rewards

| Dune | Allium | Notes |
|------|--------|-------|
| `solana.rewards` | `solana.raw.rewards` | Column `recipient` → `pubkey` |
| N/A (Dune uses `http_get()` for Jito API) | `solana.staking.rewards` with `reward_type = 'jito_mev'` | Allium has MEV rewards on-chain |

### Token Supply / Balances

| Dune | Allium | Notes |
|------|--------|-------|
| N/A | `solana.snapshots.token_supply` | Historical token supply snapshots. Columns: `mint`, `slot`, `decimals`, `raw_amount`, `_created_at`. Normalize: `raw_amount / POW(10, decimals)`. Use `QUALIFY ROW_NUMBER() OVER (PARTITION BY mint, _created_at::DATE ORDER BY slot DESC) = 1` for daily snapshots. |
| N/A | `solana.assets.spl_token_balances_latest` | **Fast** current snapshot of all token balances. Columns: `ADDRESS` (owner), `MINT`, `BALANCE`. Good for current holder counts. |
| N/A | `solana.assets.spl_token_balances_daily` | Historical daily balances. **WARNING**: Very large table, GROUP BY queries time out even with mint filters. Clustered by date, not mint. Use `solana.assets.transfers` instead for historical holder analysis. |

### Staking

| Dune | Allium | Notes |
|------|--------|-------|
| N/A | `solana.staking.balances` | Delegated stake accounts |
| N/A | `solana.staking.rewards` | Staking + MEV rewards |

---

## Column Mappings

### Common Columns

| Dune | Allium | Notes |
|------|--------|-------|
| `block_time` | `block_timestamp` | |
| `tx_id` | `txn_id` | |
| `executing_account` | `program_id` | In instruction tables |
| `account_arguments` | `accounts` | Array — also shift indexing (see below) |
| `tx_signer` / `call_tx_signer` | `signers[0]` | In transactions table. Transfers table needs JOIN. |
| `tx_success` | `parent_tx_success` | On instruction tables. On transactions: `success`. |

### Prices Table Columns

| Dune (`prices.usd`) | Allium (`common.prices.hourly`) | Notes |
|------|--------|-------|
| `minute` | `timestamp` | |
| `symbol` (e.g., `'SOL'`) | `chain` + `is_native` | See pattern below |
| `blockchain IS NULL` | `is_native = true` | For native token prices |
| `contract_address` | `address` | For SPL token prices |

**Pattern: Price Joins**

```sql
-- Dune
SELECT p.price
FROM prices.usd p
WHERE p.symbol = 'SOL' AND p.blockchain IS NULL
  AND p.minute = date_trunc('hour', t.block_time)

-- Allium
SELECT p.price
FROM common.prices.hourly p
WHERE p.chain = 'solana' AND p.is_native = true
  AND p.timestamp = date_trunc('hour', t.block_timestamp)
```

### Transfers Table Columns

| Dune (`tokens_solana.transfers`) | Allium (`solana.assets.transfers`) | Notes |
|------|--------|-------|
| `amount_raw` | N/A | Allium doesn't have raw amounts |
| `amount` (needs decimals calc) | `amount` (pre-normalized) | Allium is already decimal-adjusted |
| `amount_usd` | `usd_amount` | Different pricing coverage — see KNOWN_DIFFERENCES.md |
| `token_mint_address` | `mint` | |
| `from_token_account` / `to_token_account` | `from_address` / `to_address` | |
| N/A | `transfer_type` | Filter: `'spl_token_transfer'`, `'sol_transfer'`. Exclude `'account_close'` to match Dune. |

### Decoded Instructions Columns

| Dune | Allium (`solana.decoded.instructions`) | Notes |
|------|--------|-------|
| `account_xxx` | `PARSED_DATA:data:xxx::STRING` | JSON extraction syntax |
| `data_xxx` | `PARSED_DATA:data:xxx::TYPE` | Use appropriate cast type |
| Table name encodes instruction | `NAME` column (snake_case) | e.g., `'initialize_referral_token_account'` |

---

## SQL Dialect Conversions (Trino → Snowflake)

### Array Operations

| Operation | Dune (Trino) | Allium (Snowflake) |
|-----------|--------------|---------------------|
| Array indexing | 1-based: `array[1]` | 0-based: `array[0]` |
| Array length | `cardinality(array)` | `ARRAY_SIZE(array)` |
| Unnest | `CROSS JOIN UNNEST(arr) AS t(val)` | `LATERAL FLATTEN(input => arr) f` — use `f.value` |

**Example: Array Indexing Shift**

```sql
-- Dune
CASE
  WHEN cardinality(account_arguments) = 18 THEN account_arguments[5]
  WHEN cardinality(account_arguments) = 13 THEN account_arguments[1]
END

-- Allium (subtract 1 from all indices)
CASE
  WHEN ARRAY_SIZE(accounts) = 18 THEN accounts[4]
  WHEN ARRAY_SIZE(accounts) = 13 THEN accounts[0]
END
```

**Example: UNNEST → LATERAL FLATTEN**

```sql
-- Dune
SELECT t.val
FROM my_table
CROSS JOIN UNNEST(my_array) AS t(val)

-- Allium
SELECT f.value::STRING AS val
FROM my_table,
LATERAL FLATTEN(input => my_array) f
```

### Date/Time Functions

| Operation | Dune (Trino) | Allium (Snowflake) |
|-----------|--------------|---------------------|
| Current time | `NOW()` | `CURRENT_TIMESTAMP()` |
| Interval | `INTERVAL '7' DAY` | `INTERVAL '7 days'` |
| Date truncate | `date_trunc('day', col)` | `DATE_TRUNC('day', col)` (same) |
| Timestamp literal | `timestamp '2024-01-01'` | `'2024-01-01'::TIMESTAMP` or `timestamp '2024-01-01'` (both work) |
| Date difference | `DATE_DIFF('second', ts1, ts2)` | `DATEDIFF('second', ts1, ts2)` |
| Generate date series | `sequence(start, end, interval '1' day)` | Use `TABLE(GENERATOR(ROWCOUNT => N))` — see example below |

**Example: sequence() → GENERATOR (date series)**

```sql
-- Dune (Trino): generate array of dates, then unnest
SELECT seqs.range AS dt
FROM (SELECT sequence(DATE '2024-01-01', DATE '2024-03-31', interval '1' day) AS range) seq
CROSS JOIN UNNEST(seq.range) AS seqs(range)

-- Allium (Snowflake): use GENERATOR + DATEADD
SELECT DATEADD('day', ROW_NUMBER() OVER (ORDER BY 1) - 1, '2024-01-01'::DATE) AS dt
FROM TABLE(GENERATOR(ROWCOUNT => DATEDIFF('day', '2024-01-01'::DATE, '2024-03-31'::DATE) + 1))
```

### String / Encoding Functions

| Operation | Dune (Trino) | Allium (Snowflake) |
|-----------|--------------|---------------------|
| UTF-8 decode | `FROM_UTF8(data)` | `TRY_TO_VARCHAR(data, 'UTF-8')` |
| Hex encode | `to_hex(data)` | `HEX_ENCODE(data)` |
| Byte substring | `SUBSTR(data, offset, len)` | `SUBSTR(data, offset, len)` (same, but check 0-vs-1 indexing) |

### Type Casting

| Operation | Dune (Trino) | Allium (Snowflake) |
|-----------|--------------|---------------------|
| Safe cast | `TRY_CAST(x AS type)` | `TRY_CAST(x AS type)` (same) |
| Cast | `CAST(x AS BIGINT)` | `CAST(x AS NUMBER)` or `x::NUMBER` |
| Approximate distinct | `approx_distinct(col)` | `APPROX_COUNT_DISTINCT(col)` or `HLL(col)` |

### Aggregate Functions

| Operation | Dune (Trino) | Allium (Snowflake) |
|-----------|--------------|---------------------|
| Filtered aggregate | `SUM(col) FILTER (WHERE cond)` | `SUM(CASE WHEN cond THEN col ELSE 0 END)` |
| Filtered count | `COUNT(*) FILTER (WHERE cond)` | `COUNT_IF(cond)` or `SUM(CASE WHEN cond THEN 1 ELSE 0 END)` |

**Example: FILTER (WHERE ...) → CASE WHEN**

```sql
-- Dune
SUM(q.amount_staked) FILTER (WHERE q.entity IS NOT NULL) AS amount_staked_identified

-- Allium
SUM(CASE WHEN q.entity IS NOT NULL THEN q.amount_staked ELSE 0 END) AS amount_staked_identified
```

### Dune-Specific Features

| Feature | Dune (Trino) | Allium (Snowflake) |
|---------|--------------|---------------------|
| Materialized query ref | `query_XXXXX` (reference by ID) | No equivalent — must inline the query or find equivalent Allium tables |
| UI link function | `get_href(url, text)` | N/A — just return the text, or construct markdown: `'[' \|\| text \|\| '](' \|\| url \|\| ')'` |
| HTTP fetch | `http_get(url)` | N/A — use equivalent Allium tables instead |
| Parameterized queries | `{{param_name}}` | Use Snowflake session variables or script-level substitution |

> **Note on `query_XXXXX`**: Dune allows referencing other saved queries as tables. These are materialized/cached results. When converting, you must find the upstream query's SQL and either inline it as a CTE or identify the equivalent Allium tables. There is no Allium equivalent of cross-query references.

### Misc

| Operation | Dune (Trino) | Allium (Snowflake) |
|-----------|--------------|---------------------|
| Byte length | `length(data)` | `LENGTH(data)` (same for strings) |
| Concat | `a \|\| b` | `a \|\| b` (same) |
| Coalesce | `COALESCE(a, b)` | `COALESCE(a, b)` (same) |
| String pad | `lpad(str, len, pad)` | `LPAD(str, len, pad)` (same) |
| Date extract | `year(ts)`, `month(ts)`, `day(ts)` | `YEAR(ts)`, `MONTH(ts)`, `DAY(ts)` (same) |

---

## Success Filtering Patterns

### Instructions (Outer + Inner)

```sql
-- Allium: Use parent_tx_success directly (no JOIN needed)
SELECT *
FROM solana.raw.instructions
WHERE parent_tx_success = true
  AND program_id = '{program}'

-- Dune equivalent
SELECT *
FROM solana.instruction_calls
WHERE tx_success = true
  AND executing_account = '{program}'
```

### Transactions

```sql
-- Allium
SELECT * FROM solana.raw.transactions WHERE success = true

-- Dune
SELECT * FROM solana.transactions WHERE success = true
```

### Transfers

```sql
-- Allium: transfers table has no success column — it only contains successful transfers
-- Filter by transfer_type to exclude account closures (matches Dune behavior)
SELECT *
FROM solana.assets.transfers
WHERE transfer_type IN ('spl_token_transfer', 'sol_transfer')
```

---

## Common Conversion Recipes

### Recipe: SOL Transfers to an Address

```sql
-- Dune
SELECT
    block_time,
    tx_id,
    balance_change / 1e9 AS sol_amount
FROM solana.account_activity
WHERE address = '{addr}'
  AND tx_success = true
  AND token_mint_address IS NULL  -- SOL only

-- Allium
SELECT
    block_timestamp,
    txn_id,
    amount AS sol_amount  -- already decimal-adjusted
FROM solana.assets.transfers
WHERE to_address = '{addr}'
  AND transfer_type = 'sol_transfer'
```

### Recipe: SPL Token Transfers

```sql
-- Dune
SELECT
    block_time,
    tx_id,
    amount,
    amount_usd,
    token_mint_address
FROM tokens_solana.transfers
WHERE "from" = '{addr}'

-- Allium
SELECT
    block_timestamp,
    txn_id,
    amount,       -- already decimal-adjusted
    usd_amount,
    mint
FROM solana.assets.transfers
WHERE from_address = '{addr}'
  AND transfer_type = 'spl_token_transfer'
```

### Recipe: Program Instruction Calls with Account Extraction

```sql
-- Dune
SELECT
    block_time,
    tx_id,
    account_arguments[5] AS target_account
FROM solana.instruction_calls
WHERE executing_account = '{program}'
  AND tx_success = true

-- Allium
WITH all_instructions AS (
    SELECT block_timestamp, txn_id, accounts, data, parent_tx_success
    FROM solana.raw.instructions
    WHERE parent_tx_success = true AND program_id = '{program}'
      AND block_timestamp >= '{start}' AND block_timestamp < '{end}'
    UNION ALL
    SELECT block_timestamp, txn_id, accounts, data, parent_tx_success
    FROM solana.raw.inner_instructions
    WHERE parent_tx_success = true AND program_id = '{program}'
      AND block_timestamp >= '{start}' AND block_timestamp < '{end}'
)
SELECT
    block_timestamp,
    txn_id,
    accounts[4] AS target_account  -- index shifted by -1
FROM all_instructions
```

### Recipe: Transaction Signer from Transfers

```sql
-- Dune (decoded tables include signer)
SELECT call_tx_signer, amount
FROM system_program_solana.system_program_call_Transfer
WHERE account_to = '{addr}'

-- Allium (JOIN required for signer)
SELECT t.signer, tr.amount
FROM solana.assets.transfers tr
JOIN solana.raw.transactions t ON tr.txn_id = t.txn_id
  AND t.block_timestamp >= '{start}' AND t.block_timestamp < '{end}'
WHERE tr.to_address = '{addr}'
  AND tr.transfer_type = 'sol_transfer'
  AND tr.block_timestamp >= '{start}' AND tr.block_timestamp < '{end}'
```

### Recipe: Decoded Protocol Instructions

```sql
-- Dune
SELECT
    account_referralTokenAccount,
    account_mint
FROM jupiter_solana.referral_call_initializeReferralTokenAccount
WHERE account_referralAccount = '{referral_account}'

-- Allium
SELECT
    PARSED_DATA:data:referral_token_account::STRING AS referral_token_account,
    PARSED_DATA:data:mint::STRING AS mint
FROM solana.decoded.instructions
WHERE program_id = 'REFER4ZgmyYx9c6He5XfaTMiGfdLwRnkV4RPp9t9iF3'
  AND NAME = 'initialize_referral_token_account'
  AND PARSED_DATA:data:referral_account::STRING = '{referral_account}'
```
