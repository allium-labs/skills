# Allium Skills

Give Claude (or any MCP-compatible agent) the ability to investigate onchain questions
correctly the first time — the right table, the right aggregation, the right caveats —
instead of debugging bad SQL after the fact. The [Allium MCP](https://docs.allium.so/ai/mcp)
gives an agent live access to blockchain data across 150+ chains; these skills teach it
your team's actual analytical workflow on top of that access — how to pick a source, when
a metric needs `last` instead of `sum`, which schema is current — so results are correct
and reproducible without you having to re-explain the same pitfalls every session.

Every skill's real content lives at `skills/<name>/` at the repo root — that's the single
source of truth. They're also grouped into two independently-installable Claude Code
plugins, `plugins/allium-agent/` and `plugins/allium-analyst/`, whose `skills/`
directories are symlinks back to the same `skills/<name>/` folders rather than copies —
one skill, one location, no drift between the flat repo and the plugin groupings.

- **`allium-agent`** — direct data access: the `allium` CLI (Explorer + Realtime), plus
  partner infrastructure skills (Alchemy) that complement it in the same session.
- **`allium-analyst`** — the analyst methodology on top of that access: matching a
  question to the right source, running a defensible investigation, and sector-specific
  pitfalls (RWA, stablecoins, bridges, DEX, lending).

You can install either plugin independently, both, or install specific skills directly
without the plugin system at all (see Getting Started below).

## Getting Started

1. **Get an Allium API key** — register at [app.allium.so](https://app.allium.so/) (needed
   for the `allium-data` skill and the Allium MCP; `allium-analyst`'s skills work through
   the Allium MCP directly if you already have that configured).

2. **Install the skills** — pick whichever matches your setup:

   **Any MCP-compatible client** (Claude Code, Cursor, Claude.ai, Codex, and others),
   using the generic [Agent Skills](https://agentskills.io/) installer — this pulls in
   every skill from both plugins:
   ```bash
   npx skills add allium-labs/skills --yes
   ```
   Add `--skill <name>` to install just one skill instead of everything.

   **Claude Code, as a plugin** — install one or both bundles:
   ```
   /plugin marketplace add allium-labs/skills
   /plugin install allium-agent@allium-labs
   /plugin install allium-analyst@allium-labs
   ```

3. **Try it** — ask something that needs the workflow below, for example:
   > Use the Allium skills to investigate how tokenized RWA treasury supply has grown
   > over the past 6 months, and save the query so I can share it.

   If it checks Terminal for existing coverage, picks a real table instead of guessing,
   and hands you back a saved Explorer query at the end, the skills are wired up correctly.

## `allium-agent` — data access

### `allium-data`
Query blockchain data using the `allium` CLI. Two products: Explorer (SQL analytics on Allium's data warehouse — any table, any timeframe, 150+ chains) and Realtime (3-5s freshness lookups for prices, balances, transactions, PnL, positions across 80+ chains). Supports API key, x402 micropayments, and Tempo auth.

- **Auth**: API key, x402 micropayments, or Tempo
- **Entry point**: [`skills/allium-data/SKILL.md`](skills/allium-data/SKILL.md)

### Partner skills

Contributed by ecosystem partners — see [`PARTNERS.md`](PARTNERS.md) for conventions and how to add a new one.

- **`alchemy-agentic-gateway`** — wire Alchemy into application code without an API key, using x402 or MPP with wallet-based auth and per-request payments. Built and maintained by [Alchemy](https://www.alchemy.com/). [Entry point](skills/alchemy-agentic-gateway/SKILL.md)
- **`alchemy-api`** — build production application code on Alchemy infrastructure with an Alchemy API key (EVM JSON-RPC, WebSocket subscriptions, webhooks, Account Kit, Account Abstraction, simulation, Solana, Sui gRPC). Built and maintained by [Alchemy](https://www.alchemy.com/). [Entry point](skills/alchemy-api/SKILL.md)

## `allium-analyst` — analyst methodology

Two skills that chain together for any analytical question:

### `data-matching`
Match a question to the right Allium table, metric, dashboard, or realtime endpoint before writing any SQL — defines a data contract, compares candidate sources, and proves coverage with a bounded query.

- **Entry point**: [`skills/data-matching/SKILL.md`](skills/data-matching/SKILL.md)

### `allium-investigation`
Investigate an onchain entity, protocol, market, or wallet question — check Terminal for existing coverage first, build the method from a small test to a production query, validate the result, make calibrated claims, and save reproducible Explorer queries (with an optional dashboard hand-off prompt for Allium Assistant).

- **Entry point**: [`skills/allium-investigation/SKILL.md`](skills/allium-investigation/SKILL.md)

### Sector methodology

Sector-specific pitfalls (double-counting, table/column gotchas, classification rules) that come up repeatedly in real analysis. Each one plugs into the workflow above at the `data-matching` step — use it whenever the question touches that sector.

| Skill | Covers |
|---|---|
| [`rwa-analysis`](skills/rwa-analysis/SKILL.md) | Tokenized real-world assets — treasuries, money market funds, tokenized equities, commodities |
| [`stablecoin-analysis`](skills/stablecoin-analysis/SKILL.md) | Stablecoin transfer volume, supply, holders, and geographic usage |
| [`bridge-analysis`](skills/bridge-analysis/SKILL.md) | Cross-chain bridge and messaging-protocol data (CCTP, LayerZero, Wormhole, Across) |
| [`dex-analysis`](skills/dex-analysis/SKILL.md) | DEX/AMM trades, liquidity, aggregator routing, and DEX-derived pricing |
| [`lending-analysis`](skills/lending-analysis/SKILL.md) | DeFi lending protocol deposits, borrows, liquidations, and utilization |

## Which skill should I use?

| Scenario | Skill | Plugin |
|---|---|---|
| Any Allium data query — prices, balances, transactions, PnL, custom SQL | `allium-data` | `allium-agent` |
| Pay-per-call keyless access to Alchemy infrastructure (x402/MPP) | `alchemy-agentic-gateway` | `allium-agent` |
| Build app code on Alchemy infra (RPC, webhooks, Account Kit, simulation) | `alchemy-api` | `allium-agent` |
| Picking the right table/metric/endpoint before analyzing anything | `data-matching` | `allium-analyst` |
| Investigating an entity, protocol, market, or wallet question, and saving/sharing the result | `allium-investigation` | `allium-analyst` |
| Tokenized real-world assets (treasuries, MMFs, tokenized equities) | `rwa-analysis` | `allium-analyst` |
| Stablecoin volume, supply, or holder analysis | `stablecoin-analysis` | `allium-analyst` |
| Cross-chain bridge or messaging-protocol analysis | `bridge-analysis` | `allium-analyst` |
| DEX/AMM trades, liquidity, or aggregator analysis | `dex-analysis` | `allium-analyst` |
| DeFi lending protocol analysis | `lending-analysis` | `allium-analyst` |

## Specification

These skills follow the [Agent Skills specification](https://agentskills.io/specification). See [spec/agent-skills-spec.md](spec/agent-skills-spec.md) for details.

As Claude Code plugins, `allium-agent` and `allium-analyst` follow the [plugin specification](https://code.claude.com/docs/en/plugins-reference) — see `.claude-plugin/marketplace.json` at the repo root and each plugin's own `.claude-plugin/plugin.json` under `plugins/`. Each plugin's `skills/` directory contains symlinks back to the canonical `skills/<name>/` folders at the repo root, not copies.

## Official Links

- [Developer docs](https://docs.allium.so/)
- [Agents page](https://agents.allium.so/)
- [Get an API key](https://app.allium.so/)

## License

MIT
