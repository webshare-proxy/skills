---
name: proxy-manager
version: "2.0"
description: >
  Manage Webshare proxies with the webshare CLI: list active proxies, dump the
  proxy list to a file, refresh rotating pools, read and update proxy config,
  manage IP allowlists, build proxy URLs, inspect subscription plans and usage,
  and kick off an express-checkout flow to buy more proxies. Use when the user
  wants to work with webshare.io proxies — not scraping, just provisioning and
  ops.
license: MIT
allowed-tools: Read, Write, Edit, Bash(webshare *), Bash(python *), Bash(python3 *), Bash(open *), Bash(xdg-open *)
argument-hint: "[action]"
metadata:
  category: proxy-management
  long-description: >
    Day-to-day Webshare account operations from your agent, built on the
    official webshare CLI. Identify the right plan, list or download proxies in
    the format your tools expect, build ready-to-use proxy URLs with country
    targeting and sticky sessions, manage the IP allowlist for credential-less
    use, watch usage and failures, refresh a burned pool, and open a
    pre-filled express-checkout page when you need more capacity.
  tags: [proxies, provisioning, plans, ip-auth, proxy-urls, cli]
  install: npx skills add webshare-proxy/skills --skill proxy-manager
  example-prompts:
    - "List my Webshare proxies and save them to proxies.txt"
    - "Authorize this machine's IP so my tools can use proxies without credentials"
    - "Give me five sticky-session US proxy URLs for a worker pool"
    - "What failed in my proxy traffic over the last hour?"
    - "Refresh my proxy list — too many IPs are getting blocked"
    - "Buy 100 more dedicated datacenter proxies"
  related: [proxy-optimizer, spend-audit, scraper]
---

# Webshare Proxy Manager

You help the user manage their Webshare proxy account through the `webshare`
CLI: list proxies, refresh the pool, configure auth, build proxy URLs, watch
usage, and purchase more capacity via the express-checkout flow.

## What this skill does / needs / will not do

**Does:** everything in the workflow below, through `webshare` CLI commands.

**Needs:**

1. The `webshare` CLI — install with `brew install webshare-proxy/tap/webshare`,
   or download a binary from
   <https://github.com/webshare-proxy/webshare-cli/releases>.
2. A Webshare account — sign up at <https://www.webshare.io/> (10 free
   proxies, no card required).
3. An API key from <https://dashboard.webshare.io/userapi/keys>, exported as
   `WEBSHARE_API_KEY`. Verify with `webshare whoami`.

**Will not do:**

- **Targeted replacement of individual proxies** — the CLI has no
  per-proxy replacement command. `webshare proxies refresh` replaces the
  *entire* list; for replacing specific blocked IPs point the user at the
  sibling `proxy-optimizer` skill or the dashboard.
- **Headless purchases** — checkout always finishes in the browser; the
  express-checkout script only pre-fills the page.
- Scraping. That's the `scraper` skill.

## Workflow

### Step 1: Identify the target plan

Webshare accounts can own multiple plans simultaneously. Before any action
that touches proxies, config, or IP allowlists, run:

```bash
webshare plans list
```

If there is more than one active plan, show the list (id, type, proxy count,
status) and ask which plan to operate on (use AskUserQuestion), then pass
`--plan <id>` on every subsequent command. If there is exactly one plan you
can skip asking — but still pass `--plan` explicitly so the intent is obvious
in the command history. `webshare plans show <plan-id>` gives full detail.

### Step 2: Run the action

Ask which action the user wants (use AskUserQuestion if unclear):

- **plans** — `webshare plans list` / `webshare plans show <plan-id>`
- **list** — `webshare proxies list --plan <id>` (filters: `--country us,fr`,
  `--limit N`, `--mode direct|backbone`; formats: `--format txt|csv|json`)
- **download** — `webshare proxies list --plan <id> > proxies.txt` writes the
  standard `address:port:username:password` lines most tools accept.
  `webshare proxies download` fetches the server-rendered list instead
  (`--auth sourceip` for IP-auth setups).
- **proxy-url** — `webshare proxy-url` builds ready-to-use connection URLs:
  `--country us --rotate` for per-request rotation, `--sessions 5` for a
  sticky-session worker pool, `--session <id>` to pin one.
- **config** — `webshare config show` / `webshare config set` (`--username`,
  `--password`, `--request-timeout`, `--idle-timeout`)
- **ipauth** — `webshare ipauth list` / `webshare ipauth add --current` (or an
  explicit IP) / `webshare ipauth remove <id-or-ip>`
- **stats** — `webshare stats --since 24h` (or `--hourly`);
  `webshare activity list --error '*'` shows recent failed requests
- **refresh** — `webshare proxies refresh` replaces the whole list;
  `webshare proxies replaced` shows past replacements and successors
- **buy** — open an express-checkout URL in the browser (see below)

Read `references/CLI.md` for the full flag reference and JSON output notes.

### Buying proxies (express-checkout)

Use `scripts/express_checkout.py`. It builds a dashboard URL with the right
query string and opens it in the default browser. Six presets are supported:

- `datacenter-shared` / `datacenter-semidedicated` / `datacenter-dedicated`
- `isp-shared` / `isp-semidedicated` / `isp-dedicated`  (static residential)
- `residential`  (rotating residential, shared only)

Ask the user for preset, proxy count, bandwidth (GB, datacenter/ISP only), and
countries (dict of ISO codes → count, or `ZZ` for any). Example:

```
python scripts/express_checkout.py datacenter-dedicated \
  --count 75 --bandwidth 5000 --countries ZZ=75
```

The script prints the URL and opens the browser. The user completes checkout
manually in the dashboard — there is no headless purchase path.

## Key principles

- **Never print the API key.** The CLI reads `WEBSHARE_API_KEY` from the
  environment; never echo it or paste it into commands.
- **Confirm before mutations.** `webshare proxies refresh` consumes an
  on-demand refresh and replaces every proxy — always confirm with the user
  first and let the CLI's own confirmation prompt stand (never pass `--yes`
  unless the user explicitly asked). Same care for `config set`,
  `ipauth remove` and `subusers delete`.
- **Prefer `--json` when you need to parse.** Every command supports it, and
  piped output is machine-readable automatically.
- **Country codes are ISO 3166-1 alpha-2.** `ZZ` means "any country".
- **Residential plans are backbone-only.** If `proxies list` returns nothing,
  try `--mode backbone` or `webshare proxy-url`.
