# Allium Skills

Agent Skills for integrating [Allium](https://www.allium.so/) blockchain data APIs into AI-powered applications.

## Skills

### `skills/allium-onchain-data`
Query blockchain data via Allium APIs: token prices, wallet balances, transactions, PnL, historical data, and custom SQL analytics across 70+ chains.

- **Auth**: API key in header (`X-API-KEY`)
- **Setup**: Register at [app.allium.so](https://app.allium.so/) or via the API
- **Entry point**: [`skills/allium-onchain-data/SKILL.md`](skills/allium-onchain-data/SKILL.md)

## Which skill should I use?

| Scenario | Skill |
|---|---|
| I need token prices (current, historical, OHLCV) | `allium-onchain-data` |
| I need wallet balances or transaction history | `allium-onchain-data` |
| I need on-chain analytics with custom SQL | `allium-onchain-data` |
| I need wallet PnL data | `allium-onchain-data` |
| I want to pay per call without an API key (x402) | `allium-onchain-data` (see [x402 reference](skills/allium-onchain-data/references/x402.md)) |

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
