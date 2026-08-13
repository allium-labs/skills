# Allium Skills

Agent Skills for integrating [Allium](https://www.allium.so/) blockchain data APIs into AI-powered applications, plus partner ecosystem skills that complement Allium in a single agent session.

## Data access

### `skills/allium-data`
Query blockchain data using the `allium` CLI. Two products: Explorer (SQL analytics on Allium's data warehouse — any table, any timeframe, 150+ chains) and Realtime (3-5s freshness lookups for prices, balances, transactions, PnL, positions across 80+ chains). Supports API key, x402 micropayments, and Tempo auth.

- **Auth**: API key, x402 micropayments, or Tempo
- **Setup**: Register at [app.allium.so](https://app.allium.so/) or via the API
- **Entry point**: [`skills/allium-data/SKILL.md`](skills/allium-data/SKILL.md)

## Analyst workflow

Two skills that chain together for any analytical question:

### `skills/data-matching`
Match a question to the right Allium table, metric, dashboard, or realtime endpoint before writing any SQL — defines a data contract, compares candidate sources, and proves coverage with a bounded query.

- **Entry point**: [`skills/data-matching/SKILL.md`](skills/data-matching/SKILL.md)

### `skills/allium-investigation`
Investigate an onchain entity, protocol, market, or wallet question — check Terminal for existing coverage first, build the method from a small test to a production query, validate the result, make calibrated claims, and save reproducible Explorer queries (with an optional dashboard hand-off prompt for Allium Assistant).

- **Entry point**: [`skills/allium-investigation/SKILL.md`](skills/allium-investigation/SKILL.md)

## Sector methodology

Sector-specific pitfalls (double-counting, table/column gotchas, classification rules) that come up repeatedly in real analysis. Each one plugs into the workflow above at the `data-matching` step — use it whenever the question touches that sector.

| Skill | Covers |
|---|---|
| [`skills/rwa-analysis`](skills/rwa-analysis/SKILL.md) | Tokenized real-world assets — treasuries, money market funds, tokenized equities, commodities |
| [`skills/stablecoin-analysis`](skills/stablecoin-analysis/SKILL.md) | Stablecoin transfer volume, supply, holders, and geographic usage |
| [`skills/bridge-analysis`](skills/bridge-analysis/SKILL.md) | Cross-chain bridge and messaging-protocol data (CCTP, LayerZero, Wormhole, Across) |
| [`skills/dex-analysis`](skills/dex-analysis/SKILL.md) | DEX/AMM trades, liquidity, aggregator routing, and DEX-derived pricing |
| [`skills/lending-analysis`](skills/lending-analysis/SKILL.md) | DeFi lending protocol deposits, borrows, liquidations, and utilization |

## Partner skills

Skills contributed by ecosystem partners. See [`PARTNERS.md`](PARTNERS.md) for conventions and how to add a new partner.

### `skills/alchemy-agentic-gateway`
Wire Alchemy into application code without an API key, using x402 or MPP with wallet-based auth and per-request payments. Built and maintained by [Alchemy](https://www.alchemy.com/).

- **Entry point**: [`skills/alchemy-agentic-gateway/SKILL.md`](skills/alchemy-agentic-gateway/SKILL.md)

### `skills/alchemy-api`
Build production application code on Alchemy infrastructure with an Alchemy API key. Covers EVM JSON-RPC, WebSocket subscriptions, webhooks, Account Kit, Account Abstraction, simulation, Solana, and Sui gRPC. Built and maintained by [Alchemy](https://www.alchemy.com/).

- **Entry point**: [`skills/alchemy-api/SKILL.md`](skills/alchemy-api/SKILL.md)

## Which skill should I use?

| Scenario | Skill |
|---|---|
| Any Allium data query — prices, balances, transactions, PnL, custom SQL | `allium-data` |
| Picking the right table/metric/endpoint before analyzing anything | `data-matching` |
| Investigating an entity, protocol, market, or wallet question, and saving/sharing the result | `allium-investigation` |
| Tokenized real-world assets (treasuries, MMFs, tokenized equities) | `rwa-analysis` |
| Stablecoin volume, supply, or holder analysis | `stablecoin-analysis` |
| Cross-chain bridge or messaging-protocol analysis | `bridge-analysis` |
| DEX/AMM trades, liquidity, or aggregator analysis | `dex-analysis` |
| DeFi lending protocol analysis | `lending-analysis` |
| Pay-per-call keyless access to Alchemy infrastructure (x402/MPP) | `alchemy-agentic-gateway` |
| Build app code on Alchemy infra (RPC, webhooks, Account Kit, simulation) | `alchemy-api` |

## Installation

```bash
npx skills add allium-labs/skills --yes
```

## Specification

These skills follow the [Agent Skills specification](https://agentskills.io/specification). See [spec/agent-skills-spec.md](spec/agent-skills-spec.md) for details.

## Official Links

- [Developer docs](https://docs.allium.so/)
- [Agents page](https://agents.allium.so/)
- [Get an API key](https://app.allium.so/)

## License

MIT
