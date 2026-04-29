---
id: references/node-enhanced-apis.md
name: 'Enhanced APIs (Alchemy RPC Extensions)'
description: 'Alchemy provides enhanced JSON-RPC methods (prefixed with `alchemy_`) that offer indexed, higher-level data without manual log scanning.'
tags:
  - alchemy
  - node-apis
  - evm
  - rpc
related:
  - data-simulation-api.md
updated: 2026-02-23
---
# Enhanced APIs (Alchemy RPC Extensions)

Alchemy-specific JSON-RPC methods (`alchemy_*` prefix) that provide indexed, higher-level data. These are documented in detail in their dedicated reference files.

**Base URL**: `https://<network>.g.alchemy.com/v2/$ALCHEMY_API_KEY`

---

## Method Index

For detailed parameters, request/response examples, and response schemas, see the dedicated reference files:

| Method | Description | Reference |
|--------|-------------|-----------|
| `alchemy_simulateAssetChanges` | Simulate transaction asset changes | [data-simulation-api.md](data-simulation-api.md) |
| `alchemy_simulateExecution` | Simulate with execution traces | [data-simulation-api.md](data-simulation-api.md) |
| `alchemy_simulateAssetChangesBundle` | Simulate bundle asset changes | [data-simulation-api.md](data-simulation-api.md) |
| `alchemy_simulateExecutionBundle` | Simulate bundle with traces | [data-simulation-api.md](data-simulation-api.md) |
| `alchemy_getTransactionReceipts` | Bulk receipts for a block | [node-utility-api.md](node-utility-api.md) |

---

## Quick Example

```bash
curl -s -X POST https://eth-mainnet.g.alchemy.com/v2/$ALCHEMY_API_KEY \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "alchemy_simulateAssetChanges",
    "params": [{"from":"0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045","to":"0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eB48","value":"0x0","data":"0x"}]
  }'
```

---

## Notes

- All enhanced methods use the same JSON-RPC endpoint as standard node API.
- Enhanced APIs are efficient but compute-unit metered. Prefer filters over large ranges.
- Availability varies by network. Check per-chain support.

## Other ways to access this API

This file is part of the `alchemy-api` skill — for app code that ships with an Alchemy API key. Other paths to the same data:

- **Live agent work via CLI** (preferred when `@alchemy/cli` is installed locally — see the `alchemy-cli` skill):
  ```bash
  alchemy simulate asset-changes --tx '{"from":"0xd8dA...","to":"0xA0b8...","data":"0xa9059cbb..."}'
  ```

- **Live agent work via MCP** (when MCP is wired into your client and the CLI is not installed — see the `alchemy-mcp` skill). Call `select_app` first, then `simulateAssetChanges` or `simulateExecution` (full list in the `alchemy-mcp` skill catalog).

- **App code without an API key** (autonomous agent paying per-request, or explicit x402/MPP — see the `alchemy-agentic-gateway` skill): same API exposed at `https://x402.alchemy.com/{chainNetwork}/v2` (x402) or `https://mpp.alchemy.com/{chainNetwork}/v2` (MPP).

## Official Docs
- [Enhanced APIs Overview](https://www.alchemy.com/docs/reference/enhanced-apis-overview)
