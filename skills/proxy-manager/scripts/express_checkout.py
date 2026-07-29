#!/usr/bin/env python3
"""Build a Webshare express-checkout URL and open it in the default browser.

The dashboard's /subscription/customize page accepts the full plan config as
query-string parameters. This script picks a preset (proxy type + subtype) and
lets you override the count, bandwidth, and country mix, so you can go from
"I want 75 dedicated datacenter proxies, any country" to a pre-filled checkout
page in one command.

Usage:
    python express_checkout.py <preset> [--count N] [--bandwidth N] \\
        [--countries CC=N,CC=N,...] [--yearly] [--no-open]

Presets:
    datacenter-shared         Shared datacenter (cheapest entry tier)
    datacenter-semidedicated  Semi-dedicated datacenter, premium
    datacenter-dedicated      Dedicated datacenter, premium
    isp-shared                Shared static residential (ISP)
    isp-semidedicated         Semi-dedicated static residential (ISP)
    isp-dedicated             Dedicated static residential (ISP)
    residential               Rotating residential (shared pool, pay-per-GB)

Countries format: `US=10,FR=5,ZZ=10` where ZZ means "any country". Sum should
match --count (the dashboard will validate).
"""

import argparse
import json
import sys
import urllib.parse
import webbrowser

BASE_URL = "https://dashboard.webshare.io/subscription/customize"

COMMON = {
    "source": "multiplan-choose-plan-type",
    "isCustomSubuserCount": False,
    "siteChecks": [],
    "customSubuserCount": 0,
    "subuserCount": 3,
    "isUnlimitedIpAuthorizations": False,
    "isHighConcurrency": False,
    "isHighPriorityNetwork": False,
    "isHighIpReputation": False,
    "onDemandRefreshes": 0,
    "isCustomPlan": False,
}

PRESETS = {
    "datacenter-shared": {
        "fixed": {
            "planId": 6, "proxyType": "shared", "proxySubtype": "default",
            "behavior": "upgrade", "proxyReplacements": 10,
            "autoRefreshFrequency": 604800,
        },
        "defaults": {"count": 2, "bandwidth": 500, "countries": {"FR": 1, "US": 1, "ZZ": 0}},
    },
    "datacenter-semidedicated": {
        "fixed": {
            "planId": 6, "proxyType": "semidedicated", "proxySubtype": "premium",
            "behavior": "upgrade", "proxyReplacements": 10, "customPlanType": "",
            "autoRefreshFrequency": 0,
        },
        "defaults": {"count": 25, "bandwidth": 5000, "countries": {"ZZ": 25}},
    },
    "datacenter-dedicated": {
        "fixed": {
            "planId": 6, "proxyType": "dedicated", "proxySubtype": "premium",
            "behavior": "upgrade", "proxyReplacements": 10, "customPlanType": "",
            "autoRefreshFrequency": 0,
        },
        "defaults": {"count": 75, "bandwidth": 5000, "countries": {"ZZ": 75}},
    },
    "isp-shared": {
        "fixed": {
            "proxyType": "shared", "proxySubtype": "isp",
            "behavior": "add", "proxyReplacements": 10,
            "autoRefreshFrequency": 0,
        },
        "defaults": {"count": 50, "bandwidth": 5000, "countries": {"ZZ": 50}},
    },
    "isp-semidedicated": {
        "fixed": {
            "proxyType": "semidedicated", "proxySubtype": "isp",
            "behavior": "add", "proxyReplacements": 10, "customPlanType": "",
            "autoRefreshFrequency": 0,
        },
        "defaults": {"count": 25, "bandwidth": 5000, "countries": {"ZZ": 25}},
    },
    "isp-dedicated": {
        "fixed": {
            "proxyType": "dedicated", "proxySubtype": "isp",
            "behavior": "add", "proxyReplacements": 10, "customPlanType": "",
            "autoRefreshFrequency": 0,
        },
        "defaults": {"count": 50, "bandwidth": 5000, "countries": {"ZZ": 50}},
    },
    "residential": {
        "fixed": {
            "proxyType": "shared", "proxySubtype": "residential",
            "behavior": "add", "proxyReplacements": 0,
            "autoRefreshFrequency": 0,
        },
        "defaults": {"count": 80_000_000, "bandwidth": 1, "countries": {}},
    },
}


def parse_countries(spec: str) -> dict:
    out = {}
    for pair in spec.split(","):
        pair = pair.strip()
        if not pair:
            continue
        cc, _, n = pair.partition("=")
        out[cc.upper()] = int(n)
    return out


def build_url(preset: str, count: int, bandwidth: int, countries: dict, yearly: bool) -> str:
    cfg = PRESETS[preset]
    params = {**COMMON, **cfg["fixed"]}
    params.update({
        "proxyCount": count,
        "customProxyCount": count,
        "bandwidth": bandwidth,
        "countries": countries,
        "isYearly": yearly,
    })
    # The dashboard expects each value JSON-encoded, then URL-encoded. Empty
    # strings are emitted bare (e.g. `customPlanType=`) to match the dashboard's
    # own URL format.
    def encode(v):
        if v == "":
            return ""
        return urllib.parse.quote(json.dumps(v, separators=(",", ":")), safe="")

    query = "&".join(f"{k}={encode(v)}" for k, v in params.items())
    return f"{BASE_URL}?{query}"


def main():
    p = argparse.ArgumentParser(
        description="Generate a Webshare express-checkout URL and open it in the browser.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("preset", choices=sorted(PRESETS))
    p.add_argument("--count", type=int, help="Number of proxies")
    p.add_argument("--bandwidth", type=int, help="Bandwidth (dashboard units, usually GB)")
    p.add_argument("--countries", help="e.g. 'US=10,FR=5,ZZ=10'  (ZZ = any)")
    p.add_argument("--yearly", action="store_true", help="Yearly billing instead of monthly")
    p.add_argument("--no-open", action="store_true", help="Print URL but don't launch browser")
    args = p.parse_args()

    defaults = PRESETS[args.preset]["defaults"]
    countries = parse_countries(args.countries) if args.countries else defaults["countries"]
    url = build_url(
        args.preset,
        args.count if args.count is not None else defaults["count"],
        args.bandwidth if args.bandwidth is not None else defaults["bandwidth"],
        countries,
        args.yearly,
    )

    print(url)
    if not args.no_open:
        if not webbrowser.open(url):
            print("Could not open a browser. Copy the URL above.", file=sys.stderr)


if __name__ == "__main__":
    main()
