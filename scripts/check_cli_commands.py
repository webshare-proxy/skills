#!/usr/bin/env python3
"""Verify that every `webshare ...` invocation in the skills exists in the CLI.

Builds the real command tree by walking `webshare --help` recursively, then
extracts every webshare invocation from fenced code blocks in the skills'
markdown and from the helper scripts, and checks that each referenced
subcommand and flag actually exists. CI runs this so a skill referencing a
command the CLI does not have fails the build.

The binary is found via --cli, the WEBSHARE_CLI env var, or `webshare` on
PATH. Only --help output is used — no API key is needed.

Usage:
    python3 scripts/check_cli_commands.py
    python3 scripts/check_cli_commands.py --cli /path/to/webshare
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

WORD = re.compile(r"^[a-z][a-z0-9-]*$")
FLAG = re.compile(r"^--([a-z][a-z0-9-]*)")
# Tokens that end a single webshare invocation inside shell text.
STOP_TOKENS = {"|", "||", "&&", ";", ")", ">", ">>", "<", "2>", "2>&1", "#"}


def run_help(cli, path):
    result = subprocess.run(
        [cli, *path, "--help"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def parse_help(text):
    """Return (children, flags) parsed from one --help output."""
    children = set()
    flags = set()
    section = None
    for line in text.splitlines():
        if line.rstrip().endswith("Commands:"):
            section = "commands"
            continue
        if line.strip() in ("Flags:", "Global Flags:"):
            section = "flags"
            continue
        if not line.startswith(" "):
            section = None
            continue
        if section == "commands":
            m = re.match(r"^\s+([a-z][a-z0-9-]*)\s", line)
            if m:
                children.add(m.group(1))
        elif section == "flags":
            m = re.search(r"--([a-z][a-z0-9-]*)", line)
            if m:
                flags.add(m.group(1))
    flags.add("help")
    return children, flags


def build_tree(cli):
    """Map command path tuple -> {'children': set, 'flags': set}."""
    tree = {}

    def walk(path):
        text = run_help(cli, list(path))
        if text is None:
            return
        children, flags = parse_help(text)
        tree[path] = {"children": children, "flags": flags}
        for child in children:
            if child in ("help", "completion"):
                continue
            walk(path + (child,))

    walk(())
    if not tree:
        sys.exit(f"error: could not get help output from {cli}")
    return tree


def extract_invocations(text):
    """Yield token lists, one per `webshare ...` occurrence."""
    for m in re.finditer(r"(?<![\w/-])webshare\s+(.*)", text):
        rest = m.group(1)
        # Cut at characters that clearly end the invocation.
        rest = re.split(r"[\"'`)\n]", rest)[0]
        tokens = []
        for tok in rest.split():
            if tok in STOP_TOKENS or tok.startswith("$("):
                break
            tokens.append(tok)
        if tokens:
            yield tokens


def fenced_blocks(markdown):
    return re.findall(r"```[a-z]*\n(.*?)```", markdown, flags=re.DOTALL)


def check_invocation(tokens, tree, source):
    """Return a list of error strings for one invocation."""
    path = ()
    i = 0
    while i < len(tokens) and WORD.match(tokens[i]):
        candidate = tokens[i]
        node = tree.get(path)
        if candidate in node["children"]:
            path = path + (candidate,)
            i += 1
            continue
        if not path:
            return [f"{source}: unknown command 'webshare {candidate}'"]
        if tree[path]["children"]:
            # A command group followed by a word that is not one of its
            # subcommands is a broken reference.
            return [f"{source}: 'webshare {' '.join(path)}' has no "
                    f"subcommand '{candidate}'"]
        break  # leaf command; remaining words are positional args

    if path == ("help",) or path == ("completion",):
        return []

    errors = []
    flags = tree.get(path, tree[()])["flags"] | tree[()]["flags"]
    for tok in tokens[i:]:
        m = FLAG.match(tok)
        if m and m.group(1) not in flags:
            errors.append(f"{source}: 'webshare {' '.join(path)}' has no "
                          f"flag '--{m.group(1)}'")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", default=os.environ.get("WEBSHARE_CLI")
                        or shutil.which("webshare"),
                        help="path to the webshare binary")
    args = parser.parse_args()
    if not args.cli:
        sys.exit("error: webshare binary not found; pass --cli or set "
                 "WEBSHARE_CLI, or `go install "
                 "github.com/webshare-proxy/webshare-cli@latest`")

    tree = build_tree(args.cli)

    checked = 0
    errors = []
    skills_dir = REPO_ROOT / "skills"
    skill_dirs = [d for d in skills_dir.iterdir()
                  if d.is_dir() and (d / "SKILL.md").is_file()] \
        if skills_dir.is_dir() else []
    for skill_dir in sorted(skill_dirs):
        for file in sorted(skill_dir.rglob("*")):
            if file.suffix not in (".md", ".py"):
                continue
            text = file.read_text(encoding="utf-8")
            if file.suffix == ".md":
                text = "\n".join(fenced_blocks(text))
            source = file.relative_to(REPO_ROOT)
            for tokens in extract_invocations(text):
                checked += 1
                errors.extend(check_invocation(tokens, tree, source))

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    print(f"checked {checked} webshare invocations across "
          f"{len(skill_dirs)} skills: "
          + ("FAIL" if errors else "all commands and flags exist"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
