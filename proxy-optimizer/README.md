# Target Site Proxy Optimizer

An AI-agent-driven tool that tests your Webshare proxies against a target website, identifies which proxies are blocked (by country, ASN, or subnet), and replaces them using the Webshare MCP.

## Setup

### 1. Get a Webshare API key

Generate one at https://dashboard.webshare.io/userapi/keys

### 2. Connect the Webshare MCP to Claude Code

```bash
claude mcp add --transport http webshare https://mcp.webshare.io/ \
  -H "Authorization: Token YOUR_WEBSHARE_API_KEY"
```

### 3. Set the API key for the script

```bash
export WEBSHARE_API_KEY="your-api-key-here"
```

### 4. Install the Claude Code skill

```bash
claude plugin add /path/to/webshare-proxy-optimizer
```

Then use it:

```
/optimize-proxies https://www.example.com
```

## Quick Start (without the skill)

```bash
# Test all proxies against a target site
python optimize_proxies.py --target https://www.example.com

# Test a sample of 20 proxies with faster timeout
python optimize_proxies.py --target https://www.example.com --sample 20 --timeout 10

# Specify a plan ID (auto-detected if omitted)
python optimize_proxies.py --target https://www.example.com --plan-id 12345
```

## What It Does

1. **Fetches** your proxy list from Webshare (IPs, ports, credentials, country, ASN, subnet)
2. **Tests** each proxy against your target URL in parallel
3. **Analyzes** failures grouped by country, ASN, and /24 subnet
4. **Outputs** structured JSON with:
   - Success/failure rate per proxy
   - Problem countries, ASNs, and subnets ranked by failure rate
   - Ready-to-use MCP replacement actions

## Agent Workflow

After running the script, the agent:

1. Reports the summary (success rate, problem countries/ASNs)
2. Asks if you want to see which proxies are failing
3. Shows a table of failing proxies with IP, country, ASN, error, and latency
4. Asks which proxies to replace (all, some, or none)
5. Runs a dry-run replacement via the Webshare MCP
6. Asks for confirmation before executing
7. Re-runs the test to verify the fix

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--target` | required | URL to test proxies against |
| `--plan-id` | auto | Webshare plan ID (auto-detects active paid plan) |
| `--timeout` | 15 | Request timeout in seconds |
| `--workers` | 10 | Number of concurrent test workers |
| `--sample` | all | Test only N random proxies |

## Requirements

- Python 3.10+
- A Webshare account with an active paid plan (replacement credits needed for replacements)
- Claude Code with the Webshare MCP connected
