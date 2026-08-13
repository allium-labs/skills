# Partner Skills

This repository hosts both first-party Allium skills and skills contributed by ecosystem partners. Partner skills broaden the capabilities available to a single agent session — for example, complementing Allium's analytics with infrastructure primitives an Allium customer is likely to need alongside.

## Current partners

- **Alchemy** — `alchemy-agentic-gateway`, `alchemy-api`

## Conventions

Partner skills live alongside first-party skills under `plugins/allium-agent/skills/` with a vendor-prefixed directory name (e.g. `plugins/allium-agent/skills/alchemy-api/`) — that's the plugin bundle for direct data/infra access, distinct from `plugins/allium-analyst/` (analyst methodology). Each partner skill includes:

- `SKILL.md` with standard frontmatter plus `scope_in` / `scope_out` fields that describe what the skill is for and which sibling skill is the right pick for adjacent capabilities. These fields keep routing clean across the four-skill set without changing the skill body.
- `LICENSE.txt` reflecting the partner's license (typically MIT). Partner skills retain their original copyright.
- `metadata.author` in frontmatter naming the upstream provider.

Reference content (`references/`, `rules/`, `agents/`) is sourced from upstream and curated where needed to keep the routing matrix coherent across all skills in the repo. The editorial layer (frontmatter, light reference pruning) is regenerated when upstream changes.

## Adding a new partner

1. Open an issue describing the partner and the skill(s) being added.
2. Copy the partner's skill directory under `plugins/allium-agent/skills/<vendor>-<skill-name>/` with their LICENSE.txt and `metadata.author` preserved.
3. Add `scope_in` / `scope_out` to the SKILL.md frontmatter so routing stays clear across all skills in the repo.
4. Add the partner to the **Current partners** list above and update `README.md`'s routing table.
