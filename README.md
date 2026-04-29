# Allium Skills

Agent Skills for integrating [Allium](https://www.allium.so/) blockchain data APIs into AI-powered applications, plus partner ecosystem skills that complement Allium in a single agent session.

## Skills

### `skills/allium-onchain-data`
Query blockchain data via Allium APIs: token prices, wallet balances, transactions, PnL, historical data, and custom SQL analytics across 70+ chains.

- **Auth**: API key in header (`X-API-KEY`)
- **Setup**: Register at [app.allium.so](https://app.allium.so/) or via the API
- **Entry point**: [`skills/allium-onchain-data/SKILL.md`](skills/allium-onchain-data/SKILL.md)

### `skills/allium-x402`
Pay-per-call keyless access to Allium via the `allium` CLI. Supports API key, x402 micropayments, and Tempo auth.

- **Entry point**: [`skills/allium-x402/SKILL.md`](skills/allium-x402/SKILL.md)

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
| Token prices, wallet balances, transaction history, PnL, custom SQL | `allium-onchain-data` |
| Pay-per-call keyless access to Allium (x402) | `allium-x402` |
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
