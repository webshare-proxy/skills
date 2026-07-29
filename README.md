# Webshare Skills

The official catalog of [Agent Skills](https://agentskills.io/) for
[Webshare](https://www.webshare.io/) proxies. Works with Claude Code, Cursor,
and any agent that supports the open Agent Skills standard.

| Skill | Category | Purpose |
|---|---|---|
| [`proxy-manager`](./skills/proxy-manager) | proxy-management | Manage a Webshare account with the `webshare` CLI: list/download proxies, build proxy URLs, IP allowlists, config, usage, buying more |
| [`proxy-optimizer`](./skills/proxy-optimizer) | proxy-management | Test your proxies against a specific target site, find blocked IPs by country/ASN/subnet, and replace exactly those |
| [`scraper`](./skills/scraper) | scraping | Build production-ready Playwright scrapers (Python or Node.js) with proxy support, stealth mode, and data storage |
| [`spend-audit`](./skills/spend-audit) | cost-optimization | Read-only audit of what you pay for vs. what you use, with dollar-quantified right-sizing recommendations |

## What is a skill?

A skill is a folder with a `SKILL.md` — instructions an agent loads when a
matching task comes up, plus any helper scripts and reference docs it needs.
Installing one teaches your agent a Webshare workflow: it knows which
commands to run, what to confirm with you first, and what it must not do.

## Installation

With the [skills CLI](https://github.com/vercel-labs/skills) (Claude Code,
Cursor, and any agent supporting the Agent Skills standard):

```bash
npx skills add webshare-proxy/skills            # pick interactively
npx skills add webshare-proxy/skills --skill proxy-manager
npx skills add webshare-proxy/skills --skill proxy-optimizer
npx skills add webshare-proxy/skills --skill scraper
npx skills add webshare-proxy/skills --skill spend-audit
```

Or install the whole catalog as a Claude Code plugin — skills become
`/proxy-manager`-style shortcuts and also trigger automatically:

```
/plugin marketplace add webshare-proxy/skills
/plugin install webshare@webshare
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

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short: one directory per skill,
`SKILL.md` with the required frontmatter, author against `webshare` CLI
commands (not raw HTTP), and make CI pass.

## License

MIT, see [LICENSE](./LICENSE).
