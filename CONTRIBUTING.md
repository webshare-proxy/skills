# Contributing a skill

Adding a skill is one commit: a new directory under `skills/` with a
`SKILL.md`. CI validates everything; if it's green, the catalog picks it up.

## Layout

```
skills/your-skill/
  SKILL.md            # required — instructions + frontmatter (see below)
  scripts/            # optional helper scripts the skill runs
  references/         # optional docs the skill loads on demand
```

The directory name is the skill's slug: lowercase, digits and hyphens only.
The `skills/<name>/SKILL.md` layout is what both the
[skills CLI](https://github.com/vercel-labs/skills) and the Claude Code
plugin system expect, so the repo works as a plugin
(`/plugin marketplace add webshare-proxy/skills`) with `/your-skill`
slash-command invocation out of the box.

## SKILL.md frontmatter

The frontmatter is the source of truth for the catalog. Required shape:

```yaml
---
name: your-skill            # must equal the directory name
version: "1.0"
description: >
  What the skill does and when an agent should use it. This becomes the
  catalog's short description.
license: MIT
allowed-tools: ...          # least privilege — list only what the skill needs
metadata:
  category: proxy-management   # one of: proxy-management, scraping,
                               # cost-optimization, account
  long-description: >
    Catalog-page prose: a paragraph on what the skill actually does for the
    user, in plain language.
  tags: [lowercase, hyphenated, max-10]
  install: npx skills add webshare-proxy/skills --skill your-skill
  example-prompts:
    - "A real prompt a user would type to trigger this skill"
  related: [other-skill-slugs-in-this-catalog]
---
```

The full contract is [`schema/skill-metadata.schema.json`](./schema/skill-metadata.schema.json)
(schema version 1). If you need a new category, add it to the schema's enum in
the same PR and say why.

## Authoring rules

- **Use `webshare` CLI commands, not raw HTTP.** The CLI is substantially
  more reliable for an agent to execute than hand-rolled curl against the
  API. If the CLI can't do something the skill needs, say so explicitly in
  the skill (a "will not do" entry) rather than falling back to the API —
  and consider opening an issue on
  [webshare-cli](https://github.com/webshare-proxy/webshare-cli).
- **State the contract up front.** Every skill has a
  "What this skill does / needs / will not do" section: what it does, what it
  requires (CLI, API key, MCP, plan features), and what it refuses to do.
- **Confirm before mutations.** Anything that spends money, consumes quota,
  or replaces proxies gets an explicit user confirmation in the workflow.
- **Never print the API key.** The CLI reads `WEBSHARE_API_KEY` from the
  environment.

## The catalog index

Each skill's frontmatter `metadata:` block is the source of truth for the
Skills Catalog page in the dashboard. The schema is versioned in
[`schema/skill-metadata.schema.json`](./schema/skill-metadata.schema.json),
and the machine-readable index is generated with:

```bash
python3 scripts/build_metadata.py    # writes metadata.json
```

`metadata.json` is intentionally not committed (it's gitignored); the
dashboard developer generates and consumes it manually. CI only validates
that it *can* be built, so adding or changing a skill is just a repo commit —
a malformed skill fails the build instead of breaking the catalog page.

## Validate locally

```bash
pip install pyyaml jsonschema
python3 scripts/build_metadata.py --check     # frontmatter + schema
python3 scripts/check_cli_commands.py         # every webshare command exists
```

`check_cli_commands.py` needs the `webshare` binary
(`brew install webshare-proxy/tap/webshare`, or
`go install github.com/webshare-proxy/webshare-cli@latest` and pass
`--cli "$(go env GOPATH)/bin/webshare-cli"`). It extracts every `webshare ...`
invocation from your skill's fenced code blocks and scripts and fails on
commands or flags the CLI doesn't have.

## Verification bar

A skill isn't done when it reads well — it's done when it has been **run end
to end by an agent against a real Webshare account** and did the right thing,
including the confirmation stops. Say in the PR description which flows you
ran and what the agent did.
