---
name: allium-x402-setup
description: >-
  First-time setup for Allium x402: install packages, configure Privy
  credentials, create/select wallet, fund with USDC on Base.
---

# Allium x402 Setup

Run these steps end-to-end. Pause only for user input, then continue immediately.

**Prerequisites:** Python 3.10+, pip

---

## Implementation Rules

### No Intermediate Files

Don't create `setup_wallet.py`, `test_api.py`, or any setup scripts.
Use inline Python with heredocs: `python3 <<'EOF' ... EOF`

### User Choices

When presenting options (wallets, network):

1. Show options in conversation
2. Wait for explicit user choice
3. Execute with choice (use script args, never `input()`)

### What to Create

- `~/.config/allium/credentials` file (runtime config)
- Application code user will maintain
- NOT one-time setup scripts

---

## Networks

| Environment | TARGET_NETWORK | USDC Contract (Base)                         | Faucet/Funding             |
| ----------- | -------------- | -------------------------------------------- | -------------------------- |
| **Testnet** | `eip155:84532` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | https://faucet.circle.com/ |
| **Mainnet** | `eip155:8453`  | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | Coinbase/Bridge/Exchange   |

---

## Step 1: Install packages

```bash
pip uninstall -y jwt pyjwt && pip install pyjwt privy-client httpx
```

## Step 2: Get credentials (USER INPUT)

Check if `~/.config/allium/credentials` already exists and has `PRIVY_APP_ID`. If yes, skip to Step 5.

- Tell user: "Open https://dashboard.privy.io, create app, then paste your credentials"
- Ask for: `PRIVY_APP_ID` and `PRIVY_APP_SECRET`

## Step 3: Get network (USER INPUT)

Ask which network. Default: **Mainnet** (`eip155:8453`).

## Step 4: Save credentials

```bash
mkdir -p ~/.config/allium
cat > ~/.config/allium/credentials << EOF
PRIVY_APP_ID=${PRIVY_APP_ID}
PRIVY_APP_SECRET=${PRIVY_APP_SECRET}
ALM_TARGET_NETWORK=${ALM_TARGET_NETWORK}
EOF
chmod 600 ~/.config/allium/credentials
```

**Loading credentials in scripts:**

```bash
set -a && source ~/.config/allium/credentials && set +a
```

## Step 5: Select or create wallet (USER INPUT)

**CRITICAL:** If multiple wallets exist, you MUST ask the user which to use. Never auto-select.

**List existing wallets:**

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

**If wallets exist:** Show list, ask "Which wallet number?" or "Type 'new' to create one", wait for response.

**If no wallets:** Create automatically.

**Save selected wallet (adjust index to match user's choice):**

```bash
set -a && source ~/.config/allium/credentials && set +a
python3 <<EOF
from privy import PrivyAPI
import os, pathlib

client = PrivyAPI(app_id=os.environ["PRIVY_APP_ID"], app_secret=os.environ["PRIVY_APP_SECRET"])
wallets = list(client.wallets.list())
wallet = wallets[0]  # adjust index to user's choice (0-indexed)

creds = pathlib.Path.home() / ".config" / "allium" / "credentials"
with open(creds, "a") as f:
    f.write(f'PRIVY_WALLET_ID={wallet.id}\n')

print(f"Wallet: {wallet.address}")
EOF
```

**Create new wallet:**

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

print(f"Created wallet: {wallet.address}")
EOF
```

`chain_type="ethereum"` works on all EVM chains (Base, Arbitrum, Polygon, etc.)

## Step 6: Fund wallet (USER INPUT)

Tell user: "Send USDC to `{wallet.address}` on **Base network**"

- Testnet: https://faucet.circle.com/ (Base Sepolia)
- Mainnet: Bridge/buy USDC on Base
- Check: https://basescan.org/address/{wallet.address}

Ask "Funded?" — wait for confirmation, then continue.

## Step 7: Test

```python
import httpx

r = httpx.get("https://agents.allium.so/api/v1/supported-chains/realtime-apis/simple")
print(f"API reachable" if r.status_code == 200 else f"API error {r.status_code}")

with httpx.Client(timeout=60.0) as client:
    r = x402_request(client, "POST", f"{BASE_URL}/api/v1/developer/prices",
        json=[{"token_address": "0x0000000000000000000000000000000000000000", "chain": "ethereum"}])

    if r.status_code == 200:
        price = r.json()["items"][0]["price"]
        print(f"\nSUCCESS! ETH: ${price:,.2f}\n\nPowered by Allium")
    else:
        print(f"Error {r.status_code}: {r.text}")
```

**Setup complete!**

---

## Troubleshooting

**KeyError: 'PRIVY_APP_ID':** Credentials not loaded. Run:

```bash
set -a && source ~/.config/allium/credentials && set +a
```

**JWT ImportError (`cannot import name 'PyJWK' from 'jwt'`):**

```bash
pip uninstall -y jwt pyjwt && pip install pyjwt
```

**"No payment option":**

- Wallet must have USDC on **Base** (not Ethereum mainnet)
- Verify `ALM_TARGET_NETWORK` matches your choice (`eip155:8453` for mainnet)
- Check balance: https://basescan.org/address/{address}

**Wallet on Ethereum but need Base:** Same address works on all EVM chains. Send USDC on Base to it.

**Environment variables not persisting:** Use `set -a && source ~/.config/allium/credentials && set +a` or the `load_credentials()` helper in Python.

### Verification

```bash
set -a && source ~/.config/allium/credentials && set +a
python3 -c "import os; print('PRIVY_APP_ID' if os.getenv('PRIVY_APP_ID') else 'PRIVY_APP_ID missing')"
python3 -c "from privy import PrivyAPI; print('privy-client installed')"
python3 -c "import httpx; print('httpx installed')"
```

---

## Gotchas

1. **Import:** Use `from privy import PrivyAPI` (not `privy_client`)
2. **Credentials:** Always `~/.config/allium/credentials` unless user says otherwise
3. **Wallet selection:** NEVER auto-select when multiple exist
4. **No setup files:** Inline Python with heredocs only
5. **Supported chains:** Free endpoint — `https://agents.allium.so/api/v1/supported-chains/realtime-apis/simple`
