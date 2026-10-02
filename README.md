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

### Other agents

The repository is also a [Gemini CLI](https://geminicli.com/) extension
(`gemini-extension.json`), which asks for your API key on install:

```bash
gemini extensions install https://github.com/webshare-proxy/skills
```

GitHub Copilot CLI reads the same plugin manifest:

```bash
copilot plugin marketplace add webshare-proxy/skills
```

### The Webshare MCP server

Installed as a Claude Code plugin or a Gemini CLI extension, the catalog also
connects the hosted [Webshare MCP server](https://apidocs.webshare.io/mcp)
(`https://mcp.webshare.io/`). You sign in to it with your Webshare account
through OAuth the first time it is used. `proxy-optimizer` uses it to replace
individual blocked IPs, which the CLI can't do yet; the other skills only need
the CLI.

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

## What the skills run, send and fetch

- **The `webshare` CLI.** Every skill calls it (`scraper` only to get proxy
  URLs). It reads `WEBSHARE_API_KEY` from your environment and sends it only to
  the Webshare API (`proxy.webshare.io`), the same as when you run the CLI
  yourself.
- **The Webshare MCP server** (`https://mcp.webshare.io/`), when installed as a
  plugin or extension. It authenticates with OAuth, and you choose read or
  write access on the consent screen.
- **`proxy-optimizer`** sends a test request to the target site you name
  through each of your proxies, to find the ones that are blocked. Replacing
  IPs uses your plan's replacement credits and always runs as a dry run first,
  for you to confirm.
- **`proxy-manager`** can open a pre-filled checkout page on
  `dashboard.webshare.io` in your browser when you ask to buy more proxies.
  It never pays for anything: you review and complete the purchase yourself.
- **`scraper`** writes a project to your disk, installs its packages
  (Playwright or patchright) from PyPI or npm when you ask it to run the
  project, and loads the site you give it in a browser, through your proxies.
- **`spend-audit`** is read-only: its command allowlist excludes every
  operation that changes the account.

Nothing else leaves your machine.

## Privacy and support

- Privacy policy: <https://www.webshare.io/privacy-policy>
- Support: [support@webshare.io](mailto:support@webshare.io)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). In short: one directory per skill,
`SKILL.md` with the required frontmatter, author against `webshare` CLI
commands (not raw HTTP), and make CI pass.

## License

MIT, see [LICENSE](./LICENSE).
