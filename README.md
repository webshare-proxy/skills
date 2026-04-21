# webshare-skills

Two [Agent Skills](https://agentskills.io/) for working with [Webshare](https://www.webshare.io/) proxies. Works with Claude Code, Cursor, and any agent that supports the open Agent Skills standard.

| Skill | Purpose |
|---|---|
| [`scraper`](./scraper) | Build web scrapers with Playwright, with Webshare proxy support baked in |
| [`proxy-manager`](./proxy-manager) | List, refresh, replace, and buy Webshare proxies via the Webshare API |

## Installation

### Claude Code

Install one or both skills into your skills directory:

```bash
# User-level (both skills)
git clone https://github.com/user/webshare-skills.git ~/.claude/skills/webshare-skills
ln -s ~/.claude/skills/webshare-skills/scraper ~/.claude/skills/scraper
ln -s ~/.claude/skills/webshare-skills/proxy-manager ~/.claude/skills/proxy-manager
```

Or install a single skill directly:

```bash
mkdir -p ~/.claude/skills/scraper
cp -R scraper/* ~/.claude/skills/scraper/
```

### Using the skills CLI

```bash
npx skills add user/webshare-skills/scraper
npx skills add user/webshare-skills/proxy-manager
```

## Skill: scraper

Give it a URL, and it will explore the website with Playwright MCP, identify the data structure, and generate a production-ready scraping script with proxy support, data storage, and optional stealth mode. Supports both Python and Node.js.

Prerequisites: Playwright MCP, a runtime (Python or Node), and proxies (recommended — the `proxy-manager` skill can help you get them).

See [scraper/SKILL.md](./scraper/SKILL.md) for the full workflow.

## Skill: proxy-manager

Manage a Webshare account from the agent: list current proxies, dump them to a
file, trigger refreshes, replace dead proxies, manage IP allowlists, inspect
subscription plans, and generate an express-checkout URL to buy more proxies in
the browser.

Prerequisites:
1. A Webshare account — sign up at [webshare.io](https://www.webshare.io/) (10 free proxies, no card required).
2. An API token from [dashboard.webshare.io/userapi/keys](https://dashboard.webshare.io/userapi/keys), exported as `WEBSHARE_API_TOKEN`.

See [proxy-manager/SKILL.md](./proxy-manager/SKILL.md) and [proxy-manager/references/API.md](./proxy-manager/references/API.md).

### Express checkout

```bash
python proxy-manager/scripts/express_checkout.py datacenter-dedicated \
  --count 75 --bandwidth 5000 --countries ZZ=75
```

Presets: `datacenter-shared`, `datacenter-semidedicated`, `datacenter-dedicated`, `isp-shared`, `isp-semidedicated`, `isp-dedicated`, `residential`. See `--help` for options.

## License

MIT
