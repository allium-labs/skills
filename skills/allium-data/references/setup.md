# Allium CLI Setup

## Step 1: Install CLI

```bash
curl -sSL http://agents.allium.so/cli/install.sh | sh
```

Verify: `allium --help`. If `allium: command not found`, add `~/.local/bin` to PATH and re-source your shell.

> **Already installed?** Some of the documented subcommands (`pnl latest`/`history`, `holdings history`, `pnl-by-token`, `positions list`, `supported-chains`) require a build newer than the 0.3.1 PyPI release. If `allium realtime <subcommand> --help` returns "no such command," upgrade:
>
> ```bash
> uv tool install --upgrade allium-cli   # uv users
> pipx upgrade allium-cli                # pipx users
> pip install --user --upgrade allium-cli  # pip users
> ```

---

## Step 2: Choose auth method

Ask the user which method to use:

| Method        | Description                              | Use when                     |
| ------------- | ---------------------------------------- | ---------------------------- |
| `api_key`     | Standard Allium API key                  | Has an existing API key      |
| `tempo`       | Tempo micropayments (chain-id 42431)     | Prefers pay-per-use          |
| `x402_key`    | x402 with raw private key (Base network) | Has a Base wallet key        |
| `x402_privy`  | x402 with Privy managed wallet           | Uses Privy for key management|

Collect the required credentials (one question per credential):

- **api_key**: API key
- **tempo / x402_key**: Private key (without 0x prefix)
- **x402_privy**: Privy App ID, App Secret, Wallet ID (one at a time)

---

## Step 3: Run setup

**API Key:**
```bash
allium auth setup --method api_key --api-key <key>
```

**Tempo:**
```bash
allium auth setup --method tempo --private-key <key> --chain-id 42431
```

**x402 raw key:**
```bash
allium auth setup --method x402_key --private-key <key> --network eip155:8453
```

**x402 Privy:**
```bash
allium auth setup --method x402_privy \
  --privy-app-id <APP_ID> \
  --privy-app-secret <APP_SECRET> \
  --privy-wallet-id <WALLET_ID> \
  --network eip155:8453
```

---

## Step 4: Verify

```bash
allium auth list
```

Confirm the new profile is active (marked with a bullet) and the method/network look correct.

---

## Step 5: Test

```bash
allium realtime prices latest --chain ethereum \
  --token-address 0x0000000000000000000000000000000000000000
```

If you see a price for ETH, setup is complete.

---

## Managing Profiles

```bash
allium auth list            # Show all profiles
allium auth use <name>      # Switch active profile
allium auth remove <name>   # Delete a profile
```

---

## Troubleshooting

- **`allium: command not found`**: Ensure `~/.local/bin` is on PATH. Re-source the shell profile.
- **Authentication errors**: Re-run setup and double-check credentials.
- **No payment option (x402)**: Wallet must have USDC on Base mainnet, not Ethereum.
