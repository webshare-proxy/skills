# Webshare MCP Use Cases

## Target Site Proxy Optimizer

**Problem**: You're scraping a specific site and some proxies get blocked — wrong country, blacklisted ASN, or banned subnet. You don't know which proxies are the problem or what to replace them with.

**What the agent does**:
1. Checks your plan size and asks if you want to test all proxies or a sample
2. Tests your proxies against the target URL in parallel
3. Maps failures to countries, ASNs, and /24 subnets
4. Identifies patterns (e.g., "ASN 36352 is 100% blocked on this site")
5. Shows you exactly which proxies are failing and why
6. Replaces them via `create_proxy_replacement` (with dry-run confirmation)
7. Re-tests to verify the fix

**Data via the webshare CLI** (`plans list`, `proxies list`); **MCP tools used for replacement**: `create_proxy_replacement`, `get_proxy_replacement`

### Example

The agent starts by asking how many proxies to test:

```
> Your plan has 100 proxies. Test all of them or a sample?
>   1. All 100 proxies (takes longer)
>   2. Sample of 20 (quick check)
>   3. Sample of 50
```

Then runs the test:

```
$ python3 scripts/optimize_proxies.py --target https://www.google.com --sample 20

Testing 20 proxies against https://www.google.com (10 workers, 15s timeout)...
  [1/20]  31.56.138.150 (DE) -> OK 200 (408ms)
  [2/20]  145.223.45.79 (NL) -> OK 200 (423ms)
  ...
  [8/20]  82.27.245.138 (ZA) -> FAIL 502 Bad Gateway (372ms)
  [15/20] 82.27.246.135 (ZA) -> FAIL 502 Bad Gateway (385ms)
  [19/20] 104.143.224.192 (GB) -> FAIL HTTP 429 (1011ms)
  ...

--- Summary ---
Success rate: 85.0% (17/20)
Failed proxies: 3
Problem countries: ZA (100.0%), GB (50.0%)
Problem ASNs: Xneelo (100.0%), Getechbrothers, Mb (50.0%)

Recommended MCP action: replace 3 proxies (10 credits available)
```

The agent asks if you want to see which proxies are failing:

```
> Want to see which proxies are failing before we replace them?

| IP              | Country | ASN                | Error           | Latency |
|-----------------|---------|--------------------|-----------------|---------|
| 82.27.245.138   | ZA      | Xneelo             | 502 Bad Gateway | 372ms   |
| 82.27.246.135   | ZA      | Xneelo             | 502 Bad Gateway | 385ms   |
| 104.143.224.192 | GB      | Getechbrothers, Mb | HTTP 429        | 1011ms  |

> Replace these proxies? (dry run first)
>   1. All 3 failing proxies
>   2. Only the 2 broken ZA proxies
>   3. Don't replace any
```

The agent does a dry run first:

```
> Dry-run preview:
>   Proxies to remove: 2
>   Proxies to add: 2
>   Credits to use: 2
>
> Proceed with replacement? [y/n]
```

After confirmation, the agent executes the replacement and re-runs the test to verify the fix.
