# webshare CLI — Command Reference

Install: `brew install webshare-proxy/tap/webshare`, or a prebuilt binary from
<https://github.com/webshare-proxy/webshare-cli/releases>.
Auth: the CLI reads `WEBSHARE_API_KEY` (create a key at
<https://dashboard.webshare.io/userapi/keys>). Verify with `webshare whoami`.
Full source: <https://github.com/webshare-proxy/webshare-cli>.

## Behavior worth knowing

- **Output adapts to the destination.** Tables on a terminal; tab-separated,
  header-less output in a pipe; `--json` everywhere for jq. `proxies list`
  additionally supports `--format txt|csv|json|table`.
- **Exit codes:** `0` success, `1` API/network error, `2` usage error.
  Errors go to stderr.
- **Plan scoping:** every plan-scoped command accepts `--plan <id>`; without
  it the account's *active* plan is used. Multi-plan accounts should always
  pass `--plan` explicitly.
- `--base-url` / `WEBSHARE_BASE_URL` points at another API environment
  (testing only).

## Commands

### Account & plans

| Command | Notes |
|---|---|
| `webshare whoami` | Account the API key belongs to |
| `webshare account` | Account, subscription and active plan at a glance |
| `webshare plans list` | Plans, active first; `--all` includes cancelled |
| `webshare plans show <plan-id>` | One plan in detail (prices, countries, refresh/replacement counts) |

### Proxies

| Command | Notes |
|---|---|
| `webshare proxies list` | `--country us,fr`, `--limit N`, `--mode direct\|backbone`, `--format txt\|csv\|json`. Default txt lines are `address:port:username:password` |
| `webshare proxies download` | Server-rendered list; `--auth username\|sourceip`, `--country`, `-o file` |
| `webshare proxies refresh` | Replaces the ENTIRE list; interactive confirmation, `-y` to skip |
| `webshare proxies replaced` | Past replacements and their successors |
| `webshare proxy-url` | Build connection URLs: `--country`, `--city`, `--rotate`, `--session <id>`, `--sessions N`, `--mode`, `--address`, `--port`, `--scheme` |

`proxies list --json` returns full proxy objects: `id` (string, e.g.
`"d-10513"`), `proxy_address`, `port`, `username`, `password`, `valid`,
`country_code`, `city_name`, `asn_name`, `asn_number`, `last_verification`.

### Config & access

| Command | Notes |
|---|---|
| `webshare config show` | Proxy credentials, timeouts, auth method |
| `webshare config set` | `--username`, `--password` (8-32 alphanum), `--request-timeout`, `--idle-timeout`; only given flags change |
| `webshare ipauth list` | Authorized IPs for credential-less use |
| `webshare ipauth add [ip]` | `--current` detects this machine's public IP |
| `webshare ipauth remove <id-or-ip>` | |
| `webshare ip` | Your current public IP |

### Usage & billing

| Command | Notes |
|---|---|
| `webshare stats` | Aggregate for a period; `--since 90m/24h/7d`, `--hourly` for the series |
| `webshare activity list` | Individual proxy requests; `--error '*'` for failures only, `--search <host>`, `--since`, `--limit` |
| `webshare activity export` | CSV export; `-o file` |
| `webshare transactions list` | Payment history; `--limit` |
| `webshare invoices download <transaction-id>` | Invoice PDF; `-o file` |

### Sub-users & notifications

| Command | Notes |
|---|---|
| `webshare subusers list` | |
| `webshare subusers create` | `--label` (required), `--bandwidth GB`, `--max-threads` |
| `webshare subusers update <id>` | Only given flags change |
| `webshare subusers delete <id>` | |
| `webshare notifications list` / `dismiss <id>` | |

## What the CLI does NOT do (as of v2.0 of this skill)

- **Targeted replacement of specific proxies** — only whole-list
  `proxies refresh`. Use the `proxy-optimizer` skill (Webshare MCP) or the
  dashboard for per-IP replacement.
- **Pricing quotes for a hypothetical configuration** — use the dashboard's
  customize page (see `scripts/express_checkout.py`).
- **Purchases** — checkout is always completed in the browser.
