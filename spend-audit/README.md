# Webshare Spend Audit

A read-only Claude Code subagent that audits a Webshare account, compares what
you **pay for** against what you **actually use**, and reports concrete,
dollar-quantified plan adjustments. Run it periodically to catch wasted spend.

## What it does

- Pulls every plan, proxy config, and 90 days of usage from the Webshare MCP server.
- Flags over-allocated countries, idle plans, oversized bandwidth/proxy counts,
  unused premium add-ons, and monthly plans that would be cheaper yearly.
- Prices every recommendation with a live quote, so each saving is a real number.
- Writes a dated report and compares it to the previous run to show a trend.

## Install

Copy the subagent file into one of:

- `~/.claude/agents/webshare-spend-audit.md` — personal, available everywhere
- `.claude/agents/webshare-spend-audit.md` — project-scoped, version-controlled

Restart the Claude Code session (or use `/agents`) so it loads.

### Prerequisite

The Webshare MCP server must be connected:

```
claude mcp add --transport http mcp-webshare-io https://mcp.webshare.io/... \
  --header "Authorization: Token $WEBSHARE_MCP_TOKEN"
```

If you name the server something other than `mcp-webshare-io`, update the
`mcp__webshare__*` entries in the subagent's `tools:` list to match — otherwise
no tools are granted and every call fails.

## Usage

Invoke it in Claude Code:

```
Use the webshare-spend-audit subagent
```

It also auto-delegates when you ask about proxy costs or savings. To run it on
a schedule, add a monthly cron job:

```
claude -p "Use the webshare-spend-audit subagent"
```

## Output

A report at `./webshare-audits/spend-audit-<YYYY-MM-DD>.md` containing:

- Headline monthly and annualized savings.
- One card per finding: evidence, recommendation, dollar impact, confidence,
  and the exact dashboard step to apply it.
- A "since last audit" section once a prior report exists.

## Safety

The subagent is **strictly read-only**. Its `tools:` whitelist excludes every
state-changing Webshare tool, so it cannot allocate countries, edit IP
authorizations, replace proxies, refresh lists, or cancel renewals. It
recommends; you decide and act.

## Tuning

Two knobs, both editable as plain text in the subagent body:

- **Lookback window** — defaults to 90 days.
- **Oversized-bandwidth threshold** — flags a plan when peak usage stays at or
  below 40% of its limit.
