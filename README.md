# Webshare Skills

The official catalog of [Agent Skills](https://agentskills.io/) for
[Webshare](https://www.webshare.io/) proxies. Works with Claude Code, Cursor,
and any agent that supports the open Agent Skills standard.

| Skill | Category | Purpose |
|---|---|---|
| [`proxy-manager`](./proxy-manager) | proxy-management | Manage a Webshare account with the `webshare` CLI: list/download proxies, build proxy URLs, IP allowlists, config, usage, buying more |
| [`proxy-optimizer`](./proxy-optimizer) | proxy-management | Test your proxies against a specific target site, find blocked IPs by country/ASN/subnet, and replace exactly those |
| [`scraper`](./scraper) | scraping | Build production-ready Playwright scrapers (Python or Node.js) with proxy support, stealth mode, and data storage |
| [`spend-audit`](./spend-audit) | cost-optimization | Read-only audit of what you pay for vs. what you use, with dollar-quantified right-sizing recommendations |

## What is a skill?

A skill is a folder with a `SKILL.md` — instructions an agent loads when a
matching task comes up, plus any helper scripts and reference docs it needs.
Installing one teaches your agent a Webshare workflow: it knows which
commands to run, what to confirm with you first, and what it must not do.

## Installation

```bash
npx skills add webshare-proxy/skills/proxy-manager
npx skills add webshare-proxy/skills/proxy-optimizer
npx skills add webshare-proxy/skills/scraper
npx skills add webshare-proxy/skills/spend-audit
```

## Prerequisites

Most skills drive the official [`webshare` CLI](https://github.com/webshare-proxy/webshare-cli):

```bash
brew install webshare-proxy/tap/webshare   # or grab a release binary
export WEBSHARE_API_KEY=your-key           # https://dashboard.webshare.io/userapi/keys
webshare whoami                            # verify
```

A Webshare account comes with 10 free proxies, no card required —
[sign up](https://www.webshare.io/).

Every skill states its own prerequisites (and what it will **not** do) at the
top of its `SKILL.md`.

## The catalog index

Each skill carries catalog metadata in its `SKILL.md` frontmatter (category,
tags, install command, example prompts, related skills). The metadata schema
is versioned in [`schema/skill-metadata.schema.json`](./schema/skill-metadata.schema.json),
and a machine-readable index is generated with:

```bash
python3 scripts/build_metadata.py    # writes metadata.json (not committed)
```

CI validates the metadata and checks that every `webshare` command a skill
references actually exists in the CLI — adding or changing a skill is just a
repo commit, and a malformed skill fails the build.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short: one directory per skill,
`SKILL.md` with the required frontmatter, author against `webshare` CLI
commands (not raw HTTP), and make CI pass.

## License

MIT, see [LICENSE](./LICENSE).

---

Previously separate repos, now consolidated here:
[`webshare-spend-audit`](https://github.com/webshare-proxy/webshare-spend-audit) →
[`spend-audit`](./spend-audit) ·
[`webshare-proxy-optimizer`](https://github.com/webshare-proxy/webshare-proxy-optimizer) →
[`proxy-optimizer`](./proxy-optimizer)
