# Assets API Reference

**Base URL:** `https://api.allium.so`
**Auth:** `X-API-KEY` header

---

### List assets

`GET /api/v1/developer/assets`

List assets.

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `cursor` | string | No | Cursor for pagination |
| `limit` | integer | No | Number of results per page (default: `100`) |

```bash
curl -X GET "https://api.allium.so/api/v1/developer/assets" \
  -H "X-API-KEY: $API_KEY"
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/assets/list-assets.md`

---

### Get assets

`POST /api/v1/developer/assets/batch`

Get assets by ID, slug, or (chain, address).

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `id` | integer or null | No |  |
| `slug` | string or null | No |  |
| `chain` | string or null | No |  |
| `address` | string or null | No |  |

```bash
curl -X POST "https://api.allium.so/api/v1/developer/assets/batch" \
  -H "X-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"id": "...", "slug": "...", "chain": "...", "address": "..."}]'
```

Detailed docs (supported chains, edge cases, response format): `GET /api/v1/docs/docs/browse?path=api/developer/assets/get-assets.md`
