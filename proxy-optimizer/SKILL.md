---
name: optimize-proxies
description: Optimize your Webshare proxy pool for a specific target website. Tests all proxies, identifies blocked IPs by country/ASN/subnet, and replaces them via the Webshare MCP. Use when proxies are failing on a site, when setting up a new scraping target, or when you want to tune your proxy pool. Invoke with a target URL as argument.
---

# Target Site Proxy Optimizer

Optimize your Webshare proxy pool for a specific target website by testing, analyzing, and replacing blocked proxies.

## Invocation

```
/optimize-proxies https://www.example.com
```

The argument is the target URL to optimize proxies for.

## Requirements

- `WEBSHARE_API_KEY` environment variable must be set
- Webshare MCP server must be connected (`mcp.webshare.io`)
- Active Webshare paid plan with replacement credits (for executing replacements)

## Workflow

### Step 1: Check proxy count and ask about sampling

First, call the Webshare MCP `list_plans` tool to find the active plan and its `proxy_count`.

If the plan has more than 50 proxies, ask the user:

**"Your plan has N proxies. Test all of them or a sample?"**

Options:
- All N proxies (takes longer)
- Sample of 20 (quick check)
- Sample of 50

If 50 or fewer, skip this question and test all.

### Step 2: Run the optimizer script

Run the script from the `webshare-proxy-optimizer` directory:

```bash
WEBSHARE_API_KEY="$WEBSHARE_API_KEY" python3 optimize_proxies.py --target <TARGET_URL> --workers 10 --timeout 15
```

If the user chose a sample, add `--sample N`:

```bash
WEBSHARE_API_KEY="$WEBSHARE_API_KEY" python3 optimize_proxies.py --target <TARGET_URL> --workers 10 --timeout 15 --sample 20
```

The script outputs progress to stderr and structured JSON to stdout. Parse the JSON output.

### Step 3: Report findings

Present the results to the user:

```
Proxy Optimization Report for <TARGET_URL>

Success rate: X% (N/M proxies working)

Problem areas:
- Countries: <list countries with failure rates>
- ASNs: <list ASNs with failure rates>
- Subnets: <list /24 subnets with failure rates>

Failed proxies: <count>
Replacement credits available: <count>
```

If success rate is 100%, report that all proxies are working and no action is needed. Stop here.

### Step 4: Ask if the user wants details

Ask the user: **"Want to see which proxies are failing before we replace them?"**

If yes, show a table of every failing proxy with its IP, country, ASN, error, and latency from the `raw_results` in the JSON output. For example:

```
| IP              | Country | ASN                  | Error           | Latency |
|-----------------|---------|----------------------|-----------------|---------|
| 82.27.245.138   | ZA      | Xneelo               | 502 Bad Gateway | 396ms   |
| 82.27.246.135   | ZA      | Xneelo               | 502 Bad Gateway | 413ms   |
| 104.143.224.192 | GB      | Getechbrothers, Mb   | HTTP 429        | 808ms   |
```

Then ask: **"Replace these proxies? (dry run first)"**

If the user says no or wants to skip some, respect that. Only proceed with the IPs they confirm.

### Step 5: Dry-run replacement

If there are failures AND the user has replacement credits, execute a dry-run replacement using the Webshare MCP.

Use the `create_proxy_replacement` MCP tool with the parameters from the script's `recommendations.mcp_actions` output:

- `plan_id`: from the script output
- `to_replace`: `{"type": "ip_address", "ip_addresses": [<failed IPs>]}`
- `replace_with`: `[{"type": "any"}]`
- `dry_run`: `true`

Present the dry-run results:

```
Dry-run preview:
- Proxies to remove: <count>
- Proxies to add: <count>

Proceed with replacement? (This will use <N> replacement credits)
```

### Step 6: Execute replacement (requires user confirmation)

**CRITICAL: Always ask the user for explicit confirmation before executing.**

If the user confirms, call `create_proxy_replacement` again with `dry_run: false`.

Then poll `get_proxy_replacement` with the returned `id` until `state` is `completed` or `failed`.

### Step 7: Verify

Re-run the optimizer script against the same target to confirm the replacement improved the success rate.

Report the before/after comparison:

```
Before: X% success rate (N failures)
After:  Y% success rate (M failures)
```

## Important Rules

1. **Never skip the dry run.** Always preview before executing.
2. **Never replace without user confirmation.** Replacements consume credits and are irreversible.
3. **If replacement credits are 0**, report the findings but explain that replacements require credits (available on paid plans).
4. **If all proxies pass**, say so and stop. Don't suggest unnecessary replacements.
5. **Limit replacements to available credits.** If 20 proxies failed but only 10 credits are available, prioritize replacing proxies in the worst-performing ASNs/subnets first.

## Troubleshooting

- **`WEBSHARE_API_KEY` not set**: Tell the user to set it via `export WEBSHARE_API_KEY="..."` or generate one at https://proxy2.webshare.io/apikey
- **No active plan found**: User needs an active Webshare subscription
- **0 replacement credits**: Available on paid plans only; user may need to upgrade
- **All proxies timeout**: Target site may be completely blocking datacenter IPs; suggest trying residential proxies via `list_proxy_catalog`
