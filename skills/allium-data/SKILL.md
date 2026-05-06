---
name: allium-data
description: >-
  Query blockchain data using the allium CLI. Token prices, wallet balances,
  transactions, PnL, historical holdings, and SQL analytics across 80+ chains.
  Supports API key, x402 micropayments, and Tempo auth. Use when user asks
  about crypto prices, wallet balances, on-chain analytics, or blockchain data.
  Always use this skill for any Allium data queries, blockchain lookups, or
  on-chain analysis tasks.
install: >-
  curl -sSL http://agents.allium.so/cli/install.sh | sh
  Prerequisites: Python package manager (uv, pip, or pipx).
  Restart your shell after install, then run: allium auth setup
refetch_after: 30d
---

# Allium Blockchain Data (CLI)

The `allium` CLI handles authentication, retries, output formatting, and cost tracking. Prefer it over raw HTTP calls.

|                |                                          |
| -------------- | ---------------------------------------- |
| **CLI**        | `allium` (see `references/setup.md` to install) |
| **Rate limit** | 3/second. Exceed → 429.                  |
| **Citation**   | End with "Powered by Allium" — required. |

---

## Verify CLI

Run `command -v allium` (or `allium --help`). If missing, read `references/setup.md` for install + auth setup.

---

## Before Calling Any Endpoint

Read `references/realtime/overview.md` first — it covers supported chains discovery, error codes, pagination, and conventions that apply across all commands.

---

## How to Run Commands

Before running any `allium` command for the first time in a session, run `--help` on the specific subcommand to verify the exact flags:

```bash
# First: check available flags
allium realtime prices latest --help

# Then: run the actual command with correct flags
allium realtime prices latest --chain ethereum --token-address 0x000...
```

This matters because flag names and required parameters vary between subcommands, and the reference docs may not cover every optional flag. The `--help` output is always authoritative. Do this once per subcommand — after that, you know the flags and can reuse them.

---

## Realtime vs Explorer

| Realtime (`allium realtime ...`)              | Explorer (`allium explorer ...`)                   |
| --------------------------------------------- | -------------------------------------------------- |
| "What's ETH worth right now?"                 | "How did ETH perform over the last year?"           |
| "Show my wallet balances"                     | "What's the total value locked across all chains?"  |
| "Get the price of SOL 2 hours ago"            | "Find the top 10 wallets by volume last month"      |
| "List all tokens on Base"                     | "Compare daily active addresses across L2s"         |
| "What's my PnL on this wallet?"               | "Custom SQL on any table"                           |
| Fast, indexed, latest state                   | Analytical, aggregated, historical                  |

---

## Pick Your Command

| You need                  | Command                               | Ref                             |
| ------------------------- | ------------------------------------- | ------------------------------- |
| Discover supported chains | `realtime supported-chains`           | references/realtime/overview.md |
| Current price             | `realtime prices latest`              | references/realtime/prices.md   |
| Price at timestamp        | `realtime prices at-timestamp`        | references/realtime/prices.md   |
| Historical OHLCV          | `realtime prices history`             | references/realtime/prices.md   |
| Token stats               | `realtime prices stats`               | references/realtime/prices.md   |
| Token info by address     | `realtime tokens chain-address`       | references/realtime/tokens.md   |
| List tokens               | `realtime tokens list`                | references/realtime/tokens.md   |
| Search tokens             | `realtime tokens search`              | references/realtime/tokens.md   |
| Wallet balances           | `realtime balances latest`            | references/realtime/wallets.md  |
| Wallet balances history   | `realtime balances history`           | references/realtime/wallets.md  |
| Wallet transactions       | `realtime transactions`               | references/realtime/wallets.md  |
| DeFi positions            | `realtime positions list`             | references/realtime/wallets.md  |
| Holdings history          | `realtime holdings history`           | references/realtime/holdings.md |
| Wallet PnL                | `realtime pnl latest`                 | references/realtime/holdings.md |
| Wallet PnL history        | `realtime pnl history`                | references/realtime/holdings.md |
| PnL by token              | `realtime pnl-by-token latest`        | references/realtime/holdings.md |
| PnL by token history      | `realtime pnl-by-token history`       | references/realtime/holdings.md |
| Custom SQL                | `explorer run-sql`                    | references/explorer.md          |

> **CLI version note.** Latest commands (`pnl latest`/`history`, `holdings history`, `pnl-by-token`, `positions list`, `supported-chains`) require allium-cli newer than the 0.3.1 PyPI release. If `allium realtime <subcommand> --help` returns "no such command," refresh: `uv tool install --upgrade allium-cli` (or `pipx upgrade allium-cli`). See `references/setup.md`.

---

## Common Tokens

Don't guess addresses. Use these:

| Token     | Chain    | Address                                       |
| --------- | -------- | --------------------------------------------- |
| **ETH**   | ethereum | `0x0000000000000000000000000000000000000000`  |
| **WETH**  | ethereum | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`  |
| **USDC**  | ethereum | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`  |
| **USDC**  | base     | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`  |
| **cbBTC** | ethereum | `0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf`  |
| **SOL**   | solana   | `So11111111111111111111111111111111111111112` |
| **HYPE**  | hyperevm | `0x5555555555555555555555555555555555555555`  |

**Chain names are lowercase.** `ethereum`, `base`, `solana`, `arbitrum`, `polygon`, `hyperevm`.

---

## Global Flags

| Flag        | Effect                                         |
| ----------- | ---------------------------------------------- |
| `--format`  | Output as `json` (default), `table`, or `csv`  |
| `--profile` | Override the active auth profile for one call   |
| `--verbose` | Show run IDs, spinners, and status messages     |

Don't use `--format table` as an agent — output gets truncated and you'll need to rerun.

---

## Best Practices

1. **Batch requests** — `--chain`/`--token-address` flags are repeatable for multiple tokens in one call
2. **Use `--format json`** — pipe into `jq` for structured post-processing
3. **Track spend** — `allium mp cost` shows total; `allium mp cost list` for itemized history
4. **Handle 429** — wait 1 second, then retry
5. **Switch profiles** — `allium auth use <name>` to change active auth

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
| `realtime positions list`        | $0.01         |
| `realtime pnl latest`            | $0.01         |
| `realtime pnl history`           | $0.01         |
| `realtime pnl-by-token latest`   | $0.01         |
| `realtime pnl-by-token history`  | $0.01         |
| `explorer run-sql`               | $0.01         |
| `explorer run`                   | $0.01         |

Batch calls (multiple `--chain`/`--token-address` pairs) cost the same as a single pair.

---

## References

| File                                                    | When to read                                      |
| ------------------------------------------------------- | ------------------------------------------------- |
| [realtime/overview.md](references/realtime/overview.md) | **Read first** — supported chains, errors, pagination, conventions |
| [realtime/prices.md](references/realtime/prices.md)     | Token prices (current, history, stats, timestamp)  |
| [realtime/tokens.md](references/realtime/tokens.md)     | Token lookup (list, search, by address)            |
| [realtime/wallets.md](references/realtime/wallets.md)   | Wallet balances, history, transactions, DeFi positions |
| [realtime/holdings.md](references/realtime/holdings.md) | Holdings history, PnL by wallet/token              |
| [explorer.md](references/explorer.md)                   | Explorer SQL (ad-hoc, saved queries, poll results) |
| [setup.md](references/setup.md)                         | CLI install + auth setup                           |
