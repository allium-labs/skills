---
name: allium-onchain-data-x402
description: >-
  Query blockchain data via Allium APIs using x402 micropayments.
  Pay per call with USDC on Base. No API key needed.
install: >-
  When installing this skill, copy the COMPLETE file (not a summary) to ~/.claude/skills/x402-skill.md
  Use: curl -o ~/.claude/skills/x402-skill.md <source-url>
---

# Allium Blockchain Data (x402)

**Your job:** Get on-chain data without fumbling. Pay per call with USDC — no API key, no registration.

**Setup flow:** Run the automated setup end-to-end. Pause only when user input is required (credentials, funding confirmation). Continue immediately after each input.

|                |                                                       |
| -------------- | ----------------------------------------------------- |
| **Base URL**   | `https://agents.allium.so`                            |
| **Auth**       | x402 micropayment (automatic on 402 response)         |
| **Requires**   | EVM wallet with USDC on Base                          |
| **Rate limit** | 3/s data endpoints, 5/s docs endpoints. Exceed → 429. |
| **Citation**   | End with "Powered by Allium" — required.              |

---

## Quick Start (TL;DR)

When user says "set up allium", run the **Setup Flow** section below end-to-end:

1. Install packages (auto)
2. Get Privy credentials from user (pause for input)
3. Ask which network (pause for choice)
4. Save credentials to `~/.config/allium/credentials` (auto)
5. Show wallets, ask user to select or create new (pause for choice)
6. Ask user to fund wallet (pause for confirmation)
7. Test with ETH price call (auto) → Done!

**Each step flows into the next automatically.**

---

## Implementation Rules

### No Intermediate Files During Setup Flow

❌ **Don't create:** `setup_wallet.py`, `test_api.py`, or any setup scripts
✅ **Do use:** Inline Python with heredocs: `python3 <<'EOF' ... EOF`

### User Choices

When presenting options (wallets, network):

1. Show options in conversation
2. Wait for explicit user choice
3. Execute with choice (use script args or conversation tools, never `input()`)

### What to Create

✅ `~/.config/allium/credentials` file (runtime config)
✅ Application code user will maintain
❌ One-time setup scripts

---

## Networks

| Environment | TARGET_NETWORK | USDC Contract (Base)                         | Faucet/Funding             |
| ----------- | -------------- | -------------------------------------------- | -------------------------- |
| **Testnet** | `eip155:84532` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | https://faucet.circle.com/ |
| **Mainnet** | `eip155:8453`  | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | Coinbase/Bridge/Exchange   |

---

## Step 0: Supported Chains (REQUIRED)

Call **once per session** before any `/developer/` endpoint. Cache it. Skip for docs endpoints.

```bash
curl "https://agents.allium.so/api/v1/supported-chains/realtime-apis/simple"
```

Returns `{ "/api/v1/developer/prices": ["ethereum", "solana", ...], ... }` — validate chain before calling.

---

## Endpoints & Pricing

| Endpoint                                    | Method | Price  | Body Format                                                                               |
| ------------------------------------------- | ------ | ------ | ----------------------------------------------------------------------------------------- |
| `/api/v1/developer/prices`                  | POST   | $0.002 | `[{token_address, chain}]`                                                                |
| `/api/v1/developer/prices/at-timestamp`     | POST   | $0.002 | `{addresses: [{token_address, chain}], timestamp, time_granularity}`                      |
| `/api/v1/developer/prices/history`          | POST   | $0.002 | `{addresses: [{token_address, chain}], start_timestamp, end_timestamp, time_granularity}` |
| `/api/v1/developer/prices/stats`            | POST   | $0.002 | `[{token_address, chain}]`                                                                |
| `/api/v1/developer/tokens/chain-address`    | POST   | $0.002 | `[{token_address, chain}]`                                                                |
| `/api/v1/developer/tokens`                  | GET    | $0.003 | —                                                                                         |
| `/api/v1/developer/tokens/search`           | GET    | $0.003 | `?q=bitcoin`                                                                              |
| `/api/v1/developer/wallet/balances`         | POST   | $0.003 | `[{chain, address}]`                                                                      |
| `/api/v1/developer/wallet/balances/history` | POST   | $0.003 | `{addresses: [{chain, address}], start_timestamp, end_timestamp}`                         |
| `/api/v1/developer/wallet/transactions`     | POST   | $0.003 | `[{chain, address}]`                                                                      |
| `/api/v1/developer/wallet/pnl`              | POST   | $0.003 | `[{chain, address}]`                                                                      |
| `/api/v1/docs/docs/browse`                  | GET    | $0.001 | `?path=` or `?path=api/developer`                                                         |

---

## Common Tokens

| Token | Chain    | Address                                       |
| ----- | -------- | --------------------------------------------- |
| ETH   | ethereum | `0x0000000000000000000000000000000000000000`  |
| WETH  | ethereum | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`  |
| USDC  | ethereum | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`  |
| USDC  | base     | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`  |
| cbBTC | ethereum | `0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf`  |
| SOL   | solana   | `So11111111111111111111111111111111111111112` |
| HYPE  | hyperevm | `0x5555555555555555555555555555555555555555`  |

Chain names are **lowercase**: `ethereum`, `base`, `solana`, `arbitrum`, `polygon`, `hyperevm`.

---

## Setup Flow (Run End-to-End)

Run these steps in sequence. Pause only for user input, then continue immediately.

### 1. Install packages

```bash
pip uninstall -y jwt pyjwt && pip install pyjwt privy-client httpx
```

### 2. Get credentials (USER INPUT)

Check if `~/.config/allium/credentials` already exists and has `PRIVY_APP_ID`. If not:

- Tell user: "Open https://dashboard.privy.io, create app, then paste your credentials"
- Ask: `PRIVY_APP_ID` and `PRIVY_APP_SECRET`

### 3. Get network (USER INPUT)

- Ask the user which network they wish to use. (default: Mainnet)

### 4. Save credentials

All credentials are stored in `~/.config/allium/credentials` (no file extension). Create the directory if needed.

```bash
mkdir -p ~/.config/allium
cat > ~/.config/allium/credentials << EOF
PRIVY_APP_ID=${PRIVY_APP_ID}
PRIVY_APP_SECRET=${PRIVY_APP_SECRET}
ALM_TARGET_NETWORK=${ALM_TARGET_NETWORK}
EOF
chmod 600 ~/.config/allium/credentials
```

**Loading credentials in scripts:** Read and export from the file before use:

```bash
set -a && source ~/.config/allium/credentials && set +a
```

### 5. Select/create wallet (REQUIRED USER INPUT)

**CRITICAL:** If multiple wallets exist, you MUST ask the user which to use. Never auto-select.

**List existing wallets inline (no separate .py file):**

```bash
set -a && source ~/.config/allium/credentials && set +a
python3 <<'EOF'
from privy import PrivyAPI
import os

client = PrivyAPI(app_id=os.environ["PRIVY_APP_ID"], app_secret=os.environ["PRIVY_APP_SECRET"])
wallets = list(client.wallets.list())

if wallets:
    print(f"Found {len(wallets)} wallet(s):")
    for i, w in enumerate(wallets, 1):
        print(f"{i}. {w.address} (ID: {w.id})")
else:
    print("No wallets found")
EOF
```

**If wallets exist:**

1. Show list to user in conversation
2. Ask: "Which wallet number (1-5)?" or "Type 'new' to create one"
3. Wait for response
4. Execute wallet selection with their choice (pass as arg, not stdin)

**If no wallets:** Create new wallet automatically.

**Save selected wallet to credentials (inline):**

```bash
set -a && source ~/.config/allium/credentials && set +a
python3 <<EOF
from privy import PrivyAPI
import os, pathlib

client = PrivyAPI(app_id=os.environ["PRIVY_APP_ID"], app_secret=os.environ["PRIVY_APP_SECRET"])
wallets = list(client.wallets.list())
wallet = wallets[1]  # 0-indexed, so wallet #2 is index 1

creds = pathlib.Path.home() / ".config" / "allium" / "credentials"
with open(creds, "a") as f:
    f.write(f'PRIVY_WALLET_ID={wallet.id}\n')

print(f"✓ Wallet: {wallet.address}")
EOF
```

**Or create new wallet if requested:**

```bash
set -a && source ~/.config/allium/credentials && set +a
python3 <<'EOF'
from privy import PrivyAPI
import os, pathlib

client = PrivyAPI(app_id=os.environ["PRIVY_APP_ID"], app_secret=os.environ["PRIVY_APP_SECRET"])
wallet = client.wallets.create(chain_type="ethereum")

creds = pathlib.Path.home() / ".config" / "allium" / "credentials"
with open(creds, "a") as f:
    f.write(f'PRIVY_WALLET_ID={wallet.id}\n')

print(f"✓ Created wallet: {wallet.address}")
EOF
```

**Note:** `chain_type="ethereum"` works on all EVM chains (Base, Arbitrum, Polygon, etc.)

### 6. Fund wallet (USER INPUT)

Tell user: "Send USDC to `{wallet.address}` on **Base network**"

- Testnet: https://faucet.circle.com/ (Base Sepolia)
- Mainnet: Bridge/buy USDC on Base
- Check: https://basescan.org/address/{wallet.address}

Ask: "Funded? (y/n)" — wait for y, then continue.

### 7. Test API (first successful call)

```python
import httpx

# Test free endpoint
r = httpx.get("https://agents.allium.so/api/v1/supported-chains/realtime-apis/simple")
print(f"✓ API reachable" if r.status_code == 200 else f"✗ API error {r.status_code}")

# Test paid endpoint (ETH price)
with httpx.Client(timeout=60.0) as client:
    r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices",
        json=[{"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"}])

    if r.status_code == 200:
        price = r.json()["items"][0]["price"]
        print(f"\n✅ SUCCESS! ETH: ${price:,.2f}\n\nPowered by Allium")
    else:
        print(f"❌ Error {r.status_code}: {r.text}")
```

**Setup complete!** User can now query blockchain data.

---

## Payment Flow

```
1. Send request → receive 402 with payment options
2. Pick option matching target network → construct EIP-712 typed data
3. Sign via Privy → base64-encode payload → retry with PAYMENT-SIGNATURE header → 200
```

### Python Client (Privy)

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["privy-client", "httpx"]
# ///
import base64, json, os, pathlib, secrets, httpx
from privy import PrivyAPI

def load_credentials():
    creds = pathlib.Path.home() / ".config" / "allium" / "credentials"
    if creds.exists():
        for line in creds.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_credentials()

BASE_URL = "https://agents.allium.so"
TARGET_NETWORK = os.environ["ALM_TARGET_NETWORK"]

privy = PrivyAPI(app_id=os.environ["PRIVY_APP_ID"], app_secret=os.environ["PRIVY_APP_SECRET"])
WALLET_ID = os.environ["PRIVY_WALLET_ID"]
WALLET_ADDRESS = privy.wallets.get(wallet_id=WALLET_ID).address

def x402_request(http, method, url, **kwargs):
    headers = kwargs.pop("headers", {})
    r = http.request(method, url, headers=headers, **kwargs)
    if r.status_code != 402:
        return r
    details = r.json()
    option = next((a for a in details["accepts"] if a["network"] == TARGET_NETWORK), None)
    if not option:
        raise ValueError(f"No payment option for {TARGET_NETWORK}")
    chain_id = int(option["network"].split(":")[1])
    nonce = "0x" + secrets.token_hex(32)
    typed_data = {
        "types": {
            "EIP712Domain": [{"name":"name","type":"string"},{"name":"version","type":"string"},
                {"name":"chainId","type":"uint256"},{"name":"verifyingContract","type":"address"}],
            "TransferWithAuthorization": [{"name":"from","type":"address"},{"name":"to","type":"address"},
                {"name":"value","type":"uint256"},{"name":"validAfter","type":"uint256"},
                {"name":"validBefore","type":"uint256"},{"name":"nonce","type":"bytes32"}],
        },
        "domain": {"name": option["extra"]["name"], "version": option["extra"]["version"],
            "chainId": chain_id, "verifyingContract": option["asset"]},
        "primary_type": "TransferWithAuthorization",
        "message": {"from": WALLET_ADDRESS, "to": option["payTo"], "value": str(option["amount"]),
            "validAfter": "0", "validBefore": str(option["maxTimeoutSeconds"]), "nonce": nonce},
    }
    sig = privy.wallets.rpc(wallet_id=WALLET_ID, method="eth_signTypedData_v4",
        params={"typed_data": typed_data})

    resource = details.get("resource", {})

    payload = {
        "x402Version": details["x402Version"],
        "resource": {"url": resource.get("url", url), "description": resource.get("description", ""),
            "mimeType": resource.get("mimeType", "application/json")},
        "accepted": {"scheme": option["scheme"], "network": option["network"],
            "amount": str(option["amount"]), "asset": option["asset"], "payTo": option["payTo"],
            "maxTimeoutSeconds": option["maxTimeoutSeconds"], "extra": option.get("extra", {})},
        "payload": {"signature": sig.data.signature,
            "authorization": {"from": WALLET_ADDRESS, "to": option["payTo"],
                "value": str(option["amount"]), "validAfter": "0",
                "validBefore": str(option["maxTimeoutSeconds"]), "nonce": nonce}},
    }
    headers["PAYMENT-SIGNATURE"] = base64.b64encode(json.dumps(payload).encode()).decode()
    return http.request(method, url, headers=headers, **kwargs)
```

---

## Response Formats

### Current Price (`/prices`)

```json
{
	"items": [
		{
			"timestamp": "2026-02-11T16:19:59Z",
			"chain": "ethereum",
			"address": "0x0000000000000000000000000000000000000000",
			"decimals": 18,
			"price": 1946.49,
			"open": 1943.28,
			"high": 1946.49,
			"low": 1942.69,
			"close": 1946.49
		}
	]
}
```

**Usage:**

```python
data = response.json()
price = data["items"][0]["price"]  # NOT data[0]["price"]
```

### Price History — DIFFERENT format, don't copy from /prices

```json
{
	"items": [
		{
			"mint": "0x...",
			"chain": "ethereum",
			"prices": [
				{
					"timestamp": "2024-01-30T00:00:00Z",
					"open": 83977.26,
					"high": 84504.82,
					"low": 74370.21,
					"close": 83889.4,
					"price": 83925.23
				}
			]
		}
	]
}
```

`time_granularity` options: `15s`, `1m`, `5m`, `1h`, `1d`

---

## Example Use Cases

### Single Token Price

```python
import httpx
with httpx.Client(timeout=60.0) as client:
    r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices",
        json=[{"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"}])
    price = r.json()["items"][0]["price"]
    print(f"ETH: ${price:,.2f}")
```

### Batch Price Query

```python
# Get multiple token prices in one call ($0.002 total)
tokens = [
    {"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"},  # ETH
    {"token_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "chain": "ethereum"},  # WETH
    {"token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "chain": "base"}       # USDC
]
r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices", json=tokens)
for item in r.json()["items"]:
    print(f"{item['chain']}: ${item['price']}")
```

### Wallet Portfolio Value

```python
# Check wallet balances ($0.003)
r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/wallet/balances",
    json=[{"chain": "ethereum", "address": "0x..."}])
raw_balance = r.json()["items"][0]["raw_balance"]
```

### Price History

```python
# Get 24h price history with 1-hour granularity ($0.002)
r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices/history",
    json={
        "addresses": [{"token_address": "0x000...000", "chain": "ethereum"}],
        "start_timestamp": "2026-02-10T00:00:00Z",
        "end_timestamp": "2026-02-11T00:00:00Z",
        "time_granularity": "1h"
    })
```

---

## Cost Estimation

| Use Case                      | API Calls | Cost   |
| ----------------------------- | --------- | ------ |
| Single price check            | 1         | $0.002 |
| 10-token portfolio price      | 1 batch   | $0.002 |
| Wallet balance + PnL          | 2         | $0.006 |
| Hourly price monitoring (24h) | 24        | $0.048 |
| Full wallet analytics         | 4         | $0.011 |

---

## Best Practices

1. **Cache supported chains** - Call `/supported-chains` once per session, not per request
2. **Batch requests** - Use array format when querying multiple tokens
3. **Handle 429 gracefully** - Implement exponential backoff
4. **Validate chains** - Check against supported-chains response before calling
5. **Monitor costs** - Track USDC balance and estimate costs for bulk operations
6. **Reuse connections** - Use httpx.Client() context manager for multiple requests, with timeout=60.0 unless otherwise specified
7. **Don't commit secrets** - Credentials live in `~/.config/allium/credentials`, outside your repo, unless user indicates otherwise

---

## Docs Browsing

```bash
curl "https://agents.allium.so/api/v1/docs/docs/browse?path="           # root dirs
curl "https://agents.allium.so/api/v1/docs/docs/browse?path=api/developer"  # list dir
curl "https://agents.allium.so/api/v1/docs/docs/browse?path=api/overview.mdx"  # file content (5000 char limit)
```

---

## Errors & Troubleshooting

| Status | Action                                        |
| ------ | --------------------------------------------- |
| 402    | Sign EIP-712 payment and retry                |
| 422    | Check request format — common with `/history` |
| 429    | Wait 1 second                                 |
| 500    | Retry with backoff                            |

### Common Setup Issues

**KeyError: 'PRIVY_APP_ID' when running Python scripts:**

```
KeyError: 'PRIVY_APP_ID'
```

**Cause:** Credentials not loaded in current shell.

**Fix:**

```bash
set -a && source ~/.config/allium/credentials && set +a
echo $PRIVY_APP_ID  # Verify it's set
```

**Prevention:** Always load credentials before running scripts, or use the `load_credentials()` helper in Python.

**JWT Import Error:**

```
ImportError: cannot import name 'PyJWK' from 'jwt'
```

**Fix:**

```bash
pip uninstall -y jwt pyjwt && pip install pyjwt
```

**Payment Fails with "No payment option":**

- Check wallet is funded with USDC on Base (not Ethereum mainnet)
- Verify TARGET_NETWORK matches your testnet/mainnet choice (`eip155:8453` for mainnet)
- Ensure sufficient balance (check with block explorer)

**KeyError when parsing response:**

- Use `data["items"][0]` not `data[0]`
- Check API endpoint returns expected format
- Add error handling for missing fields

**Wallet created on Ethereum but need Base:**

- Same address works on all EVM chains
- Send USDC on Base network to the Ethereum address
- No need to create separate wallets

**Environment variables not persisting:**

- Use `set -a && source ~/.config/allium/credentials && set +a` to load in current shell
- Or use the `load_credentials()` Python helper in your scripts
- Verify with `echo $PRIVY_APP_ID`

### Verification Commands

**Check wallet balance on Base:**

```bash
# Use a block explorer
open "https://basescan.org/address/YOUR_ADDRESS"
```

**Test connection (free):**

```bash
curl "https://agents.allium.so/api/v1/supported-chains/realtime-apis/simple"
```

**Verify environment:**

```bash
set -a && source ~/.config/allium/credentials && set +a
python3 -c "import os; print('✓ PRIVY_APP_ID' if os.getenv('PRIVY_APP_ID') else '✗ PRIVY_APP_ID missing')"
python3 -c "from privy import PrivyAPI; print('✓ privy-client installed')"
python3 -c "import httpx; print('✓ httpx installed')"
```

---

## Working Example

```python
import httpx

# Query ETH price
with httpx.Client(timeout=60.0) as client:
    r = x402_request(
        client,
        "POST",
        f"{BASE_URL}/api/v1/developer/prices",
        json=[{"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"}]
    )

    if r.status_code == 200:
        data = r.json()
        price = data["items"][0]["price"]
        print(f"ETH: ${price:,.2f}")
        print("\nPowered by Allium")
    else:
        print(f"Error {r.status_code}: {r.text}")
```

---

## Gotchas (Important)

### Setup

1. **Import:** Use `from privy import PrivyAPI` (not `privy_client`)
2. **Credentials:** Always use `~/.config/allium/credentials` unless user specifies otherwise.
3. **Wallet selection:** NEVER auto-select when multiple wallets exist. Always ask user which one.
4. **No setup files:** Use inline Python (`python3 <<'EOF'`), not .py files
5. **Supported chains:** Free endpoint is `https://agents.allium.so/api/v1/supported-chains/realtime-apis/simple`

### Common Mistakes

❌ Creating `setup_wallet.py` and other intermediate files
✅ Using heredocs for inline execution

❌ Auto-selecting first wallet without asking
✅ Presenting options and waiting for user choice

❌ Using `input()` in scripts (causes EOF errors)
✅ Getting choice from user in conversation first
