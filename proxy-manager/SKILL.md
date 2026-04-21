---
name: proxy-manager
version: "1.0"
description: >
  Manage Webshare proxies via the Webshare API: list active proxies, download the
  proxy list, refresh rotating pools, replace broken proxies, read and update
  proxy config, manage IP allowlists, inspect subscription plans, and kick off an
  express-checkout flow to buy more proxies. Use when the user wants to work with
  webshare.io proxies — not scraping, just provisioning and ops.
allowed-tools: Read, Write, Edit, Bash(curl *), Bash(python *), Bash(python3 *), Bash(open *), Bash(xdg-open *)
argument-hint: "[action]"
---

# Webshare Proxy Manager

You help the user manage their Webshare proxy account: list proxies, refresh the
rotating pool, replace dead proxies, configure auth, and purchase more via the
express-checkout flow.

## Prerequisites

**API token** — required for every API call.

1. Check `WEBSHARE_API_TOKEN` in the environment. If missing, tell the user:
   > Create an API key at https://dashboard.webshare.io/userapi/keys then
   > `export WEBSHARE_API_TOKEN=<token>`.
2. All API requests use header `Authorization: Token $WEBSHARE_API_TOKEN` against
   base URL `https://proxy.webshare.io/api/v2/`.

## Workflow

### Step 1: Identify the target plan

Webshare accounts can own multiple plans simultaneously. Before any action that
touches proxies, config, or IP allowlists, call `GET /subscription/plan/` to
list the user's plans and their IDs. If there is more than one:

- Show the user the list (plan id, proxy type/subtype, count, status)
- Ask which plan they want to operate on (use AskUserQuestion)
- Pass that id as `?plan_id=<id>` on every subsequent call

If there is exactly one plan, you can skip asking — but still pass `plan_id`
explicitly so the intent is obvious in the command history.

### Step 2: Run the action

Ask which action the user wants (use AskUserQuestion if unclear):

- **plans** — list all subscription plans
- **list** — show proxies on a plan (with filters)
- **download** — dump the proxy list to a file for app consumption
- **replace** — replace specific broken proxies
- **config** — view or update proxy config (rotation, backbone, IP-auth-only)
- **ipauth** — manage the allowlist of IPs that can use the proxies
- **stats** — recent bandwidth / request counts
- **buy** — open an express-checkout URL in the browser (see below)

For every action, read `references/API.md` to get the exact endpoint, params,
and response shape. Prefer `curl` for one-shots. Fall back to Python only when
you need to parse or mutate the response.

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
manually in the dashboard — the API does not expose a headless purchase path.

## Key Principles

- **Always send the `X-Webshare-Source` header** on every API call, value
  `WebshareSkill/<frontmatter version> (LLM; <your model, e.g. Claude/Opus-4.7>)`.
- **Never print the API token.** Mask it in shell examples (`$WEBSHARE_API_TOKEN`).
- **Rate limits are tight.** Proxy-list endpoints are 60 req/min, downloads 30
  req/min. Cache responses locally during a session.
- **Respect the user's plan.** Before calling refresh/replace/upgrade, confirm
  with the user — these may consume quota or trigger a charge.
- **Country codes are ISO 3166-1 alpha-2.** Use `ZZ` to mean "any country".
