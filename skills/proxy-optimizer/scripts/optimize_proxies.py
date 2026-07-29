#!/usr/bin/env python3
"""
Target Site Proxy Optimizer

Tests all proxies in a Webshare plan against a target URL, identifies which
proxies/countries/ASNs are blocked, and outputs a structured report that an
AI agent can use to drive replacements via the Webshare MCP.

Plan and proxy data come from the webshare CLI (which reads WEBSHARE_API_KEY);
only the target-site probes talk to the network directly.

Usage:
    python optimize_proxies.py --target https://example.com
    python optimize_proxies.py --target https://example.com --plan-id 12345
    python optimize_proxies.py --target https://example.com --timeout 10 --workers 20
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict


def cli_json(*args):
    """Run a webshare CLI command with --json and return the parsed output."""
    cli = shutil.which("webshare")
    if not cli:
        print("ERROR: webshare CLI not found on PATH. Install it with "
              "`brew install webshare-proxy/tap/webshare` or from "
              "https://github.com/webshare-proxy/webshare-cli/releases",
              file=sys.stderr)
        sys.exit(1)
    result = subprocess.run([cli, *args, "--json"],
                            capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"ERROR: webshare {' '.join(args)} failed: "
              f"{result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def fetch_all_proxies(plan_id):
    proxies = cli_json("proxies", "list", "--plan", str(plan_id),
                       "--mode", "direct")
    # Residential pools have no per-proxy address; those can't be probed.
    return [p for p in proxies if p.get("proxy_address")]


def get_active_plan():
    plans = cli_json("plans", "list")
    active = [p for p in plans if p.get("status") == "active"]
    for plan in active:
        if plan.get("monthly_price", 0) > 0:
            return plan
    if active:
        return active[0]
    print("ERROR: No active plan found", file=sys.stderr)
    sys.exit(1)


def test_proxy(proxy, target_url, timeout):
    ip = proxy["proxy_address"]
    port = proxy["port"]
    user = proxy["username"]
    pw = proxy["password"]

    proxy_url = f"http://{user}:{pw}@{ip}:{port}"

    handler = urllib.request.ProxyHandler({
        "http": proxy_url,
        "https": proxy_url,
    })
    ctx = ssl.create_default_context()
    https_handler = urllib.request.HTTPSHandler(context=ctx)
    opener = urllib.request.build_opener(handler, https_handler)

    start = time.time()
    try:
        req = urllib.request.Request(target_url)
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        resp = opener.open(req, timeout=timeout)
        elapsed = time.time() - start
        status = resp.getcode()
        return {
            "proxy_address": ip,
            "port": port,
            "country_code": proxy["country_code"],
            "city_name": proxy.get("city_name", ""),
            "asn_name": proxy.get("asn_name", ""),
            "asn_number": proxy.get("asn_number"),
            "success": 200 <= status < 400,
            "status_code": status,
            "latency_ms": round(elapsed * 1000),
            "error": None,
        }
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        return {
            "proxy_address": ip,
            "port": port,
            "country_code": proxy["country_code"],
            "city_name": proxy.get("city_name", ""),
            "asn_name": proxy.get("asn_name", ""),
            "asn_number": proxy.get("asn_number"),
            "success": False,
            "status_code": e.code,
            "latency_ms": round(elapsed * 1000),
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "proxy_address": ip,
            "port": port,
            "country_code": proxy["country_code"],
            "city_name": proxy.get("city_name", ""),
            "asn_name": proxy.get("asn_name", ""),
            "asn_number": proxy.get("asn_number"),
            "success": False,
            "status_code": None,
            "latency_ms": round(elapsed * 1000),
            "error": str(e),
        }


def analyze_results(results):
    by_country = defaultdict(lambda: {"total": 0, "failed": 0, "ips": []})
    by_asn = defaultdict(lambda: {"total": 0, "failed": 0, "name": "", "ips": []})
    by_subnet = defaultdict(lambda: {"total": 0, "failed": 0, "ips": []})
    failed_ips = []

    for r in results:
        ip = r["proxy_address"]
        cc = r["country_code"]
        asn = r["asn_number"]
        asn_name = r["asn_name"]
        subnet = ".".join(ip.split(".")[:3]) + ".0/24"

        by_country[cc]["total"] += 1
        by_asn[asn]["total"] += 1
        by_asn[asn]["name"] = asn_name
        by_subnet[subnet]["total"] += 1

        if not r["success"]:
            by_country[cc]["failed"] += 1
            by_country[cc]["ips"].append(ip)
            by_asn[asn]["failed"] += 1
            by_asn[asn]["ips"].append(ip)
            by_subnet[subnet]["failed"] += 1
            by_subnet[subnet]["ips"].append(ip)
            failed_ips.append(ip)

    total = len(results)
    failed = len(failed_ips)
    success_rate = round((total - failed) / total * 100, 1) if total else 0

    problem_countries = {
        cc: {
            "total": d["total"],
            "failed": d["failed"],
            "failure_rate": round(d["failed"] / d["total"] * 100, 1),
            "failed_ips": d["ips"],
        }
        for cc, d in by_country.items()
        if d["failed"] > 0
    }

    problem_asns = {
        str(asn): {
            "name": d["name"],
            "total": d["total"],
            "failed": d["failed"],
            "failure_rate": round(d["failed"] / d["total"] * 100, 1),
            "failed_ips": d["ips"],
        }
        for asn, d in by_asn.items()
        if d["failed"] > 0
    }

    problem_subnets = {
        subnet: {
            "total": d["total"],
            "failed": d["failed"],
            "failure_rate": round(d["failed"] / d["total"] * 100, 1),
            "failed_ips": d["ips"],
        }
        for subnet, d in by_subnet.items()
        if d["failed"] > 0
    }

    problem_countries = dict(sorted(problem_countries.items(), key=lambda x: x[1]["failure_rate"], reverse=True))
    problem_asns = dict(sorted(problem_asns.items(), key=lambda x: x[1]["failure_rate"], reverse=True))
    problem_subnets = dict(sorted(problem_subnets.items(), key=lambda x: x[1]["failure_rate"], reverse=True))

    return {
        "total_proxies": total,
        "failed_proxies": failed,
        "success_rate": success_rate,
        "failed_ips": failed_ips,
        "problem_countries": problem_countries,
        "problem_asns": problem_asns,
        "problem_subnets": problem_subnets,
    }


def build_recommendations(analysis, plan):
    recs = []
    replacements_available = plan.get("proxy_replacements_available", 0)

    if analysis["failed_proxies"] == 0:
        return recs

    for asn_id, data in analysis["problem_asns"].items():
        if data["failure_rate"] == 100 and data["total"] >= 2:
            recs.append({
                "action": "replace_by_asn",
                "reason": f"ASN {data['name']} (AS{asn_id}) has 100% failure rate ({data['total']} proxies)",
                "ips_to_replace": data["failed_ips"],
                "count": len(data["failed_ips"]),
            })

    for subnet, data in analysis["problem_subnets"].items():
        if data["failure_rate"] == 100 and data["total"] >= 2:
            already_covered = any(
                set(data["failed_ips"]).issubset(set(r["ips_to_replace"]))
                for r in recs
            )
            if not already_covered:
                recs.append({
                    "action": "replace_by_subnet",
                    "reason": f"Subnet {subnet} has 100% failure rate ({data['total']} proxies)",
                    "ips_to_replace": data["failed_ips"],
                    "count": len(data["failed_ips"]),
                })

    covered_ips = set()
    for r in recs:
        covered_ips.update(r["ips_to_replace"])

    remaining = [ip for ip in analysis["failed_ips"] if ip not in covered_ips]
    if remaining:
        recs.append({
            "action": "replace_individual",
            "reason": f"{len(remaining)} additional proxy(ies) failed individually",
            "ips_to_replace": remaining,
            "count": len(remaining),
        })

    total_to_replace = sum(r["count"] for r in recs)
    return {
        "recommendations": recs,
        "total_ips_to_replace": total_to_replace,
        "replacement_credits_available": replacements_available,
        "can_replace_all": total_to_replace <= replacements_available,
        "mcp_actions": build_mcp_actions(analysis, recs),
    }


def build_mcp_actions(analysis, recs):
    all_ips = []
    for r in recs:
        all_ips.extend(r["ips_to_replace"])

    if not all_ips:
        return []

    working_countries = []
    for cc, data in analysis.get("problem_countries", {}).items():
        if data["failure_rate"] < 50:
            working_countries.append(cc)

    if not working_countries:
        replace_with = [{"type": "any"}]
    else:
        replace_with = [{"type": "country", "country_code": cc} for cc in working_countries[:3]]

    return [
        {
            "tool": "create_proxy_replacement",
            "description": f"Replace {len(all_ips)} failing proxies",
            "params": {
                "to_replace": {
                    "type": "ip_address",
                    "ip_addresses": all_ips,
                },
                "replace_with": replace_with,
                "dry_run": True,
            },
            "note": "Run with dry_run=true first, then confirm with the user before setting dry_run=false",
        }
    ]


def main():
    parser = argparse.ArgumentParser(description="Test proxies against a target site and find what to replace")
    parser.add_argument("--target", required=True, help="Target URL to test proxies against")
    parser.add_argument("--plan-id", type=int, help="Webshare plan ID (auto-detected if omitted)")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds (default: 15)")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent test workers (default: 10)")
    parser.add_argument("--sample", type=int, help="Test only N random proxies instead of all")
    args = parser.parse_args()

    print(f"Target: {args.target}", file=sys.stderr)

    if args.plan_id:
        plan = cli_json("plans", "show", str(args.plan_id))
    else:
        plan = get_active_plan()
    plan_id = plan["id"]
    print(f"Plan: {plan_id} ({plan.get('proxy_type', '?')}/{plan.get('proxy_subtype', '?')}, {plan.get('proxy_count', '?')} proxies, {plan.get('proxy_replacements_available', 0)} replacement credits)", file=sys.stderr)

    print("Fetching proxy list...", file=sys.stderr)
    proxies = fetch_all_proxies(plan_id)
    print(f"Found {len(proxies)} proxies", file=sys.stderr)

    if args.sample and args.sample < len(proxies):
        import random
        proxies = random.sample(proxies, args.sample)
        print(f"Sampling {args.sample} proxies", file=sys.stderr)

    print(f"Testing {len(proxies)} proxies against {args.target} ({args.workers} workers, {args.timeout}s timeout)...", file=sys.stderr)

    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(test_proxy, p, args.target, args.timeout): p for p in proxies}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            done += 1
            status = "OK" if result["success"] else "FAIL"
            print(f"  [{done}/{len(proxies)}] {result['proxy_address']} ({result['country_code']}) -> {status} {result.get('error') or result.get('status_code', '')} ({result['latency_ms']}ms)", file=sys.stderr)

    analysis = analyze_results(results)
    recommendations = build_recommendations(analysis, plan)

    output = {
        "target": args.target,
        "plan_id": plan_id,
        "plan_product": f"{plan.get('proxy_type', '?')}/{plan.get('proxy_subtype', '?')}",
        "summary": {
            "total_tested": analysis["total_proxies"],
            "successful": analysis["total_proxies"] - analysis["failed_proxies"],
            "failed": analysis["failed_proxies"],
            "success_rate": analysis["success_rate"],
        },
        "problem_countries": analysis["problem_countries"],
        "problem_asns": analysis["problem_asns"],
        "problem_subnets": analysis["problem_subnets"],
        "recommendations": recommendations,
        "raw_results": results,
    }

    print(json.dumps(output, indent=2))

    print(f"\n--- Summary ---", file=sys.stderr)
    print(f"Success rate: {analysis['success_rate']}% ({analysis['total_proxies'] - analysis['failed_proxies']}/{analysis['total_proxies']})", file=sys.stderr)
    if analysis["failed_proxies"] > 0:
        print(f"Failed proxies: {analysis['failed_proxies']}", file=sys.stderr)
        if analysis["problem_countries"]:
            print(f"Problem countries: {', '.join(f'{cc} ({d['failure_rate']}%)' for cc, d in analysis['problem_countries'].items())}", file=sys.stderr)
        if analysis["problem_asns"]:
            print(f"Problem ASNs: {', '.join(f'{d['name']} ({d['failure_rate']}%)' for d in analysis['problem_asns'].values())}", file=sys.stderr)
        if recommendations and recommendations.get("mcp_actions"):
            print(f"\nRecommended MCP action: replace {recommendations['total_ips_to_replace']} proxies ({recommendations['replacement_credits_available']} credits available)", file=sys.stderr)
    else:
        print("All proxies working — no action needed.", file=sys.stderr)


if __name__ == "__main__":
    main()
