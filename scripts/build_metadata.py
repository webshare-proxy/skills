#!/usr/bin/env python3
"""Build (or just validate) the catalog metadata index.

Walks every top-level directory containing a SKILL.md, reads the YAML
frontmatter, assembles the catalog entry for each skill, validates the
result against schema/skill-metadata.schema.json, and writes metadata.json
at the repo root.

metadata.json is deliberately NOT committed (see .gitignore) — the dashboard
developer generates and consumes it manually. CI runs this script with
--check so a malformed skill fails the build instead of breaking the catalog
page at runtime.

Usage:
    python3 scripts/build_metadata.py           # validate + write metadata.json
    python3 scripts/build_metadata.py --check   # validate only

Requires: pyyaml, jsonschema  (pip install pyyaml jsonschema)
"""

import argparse
import json
import sys
from pathlib import Path

import yaml
import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
SCHEMA_PATH = REPO_ROOT / "schema" / "skill-metadata.schema.json"
OUTPUT_PATH = REPO_ROOT / "metadata.json"

# Frontmatter metadata keys (kebab-case) -> catalog entry keys (snake_case).
METADATA_KEYS = {
    "category": "category",
    "tags": "tags",
    "install": "install",
    "example-prompts": "example_prompts",
    "long-description": "long_description",
    "related": "related_skills",
}


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def read_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{skill_md}: missing YAML frontmatter (file must start with ---)")
    try:
        _, fm, _ = text.split("---\n", 2)
    except ValueError:
        fail(f"{skill_md}: unterminated YAML frontmatter")
    try:
        data = yaml.safe_load(fm)
    except yaml.YAMLError as e:
        fail(f"{skill_md}: invalid YAML frontmatter: {e}")
    if not isinstance(data, dict):
        fail(f"{skill_md}: frontmatter is not a mapping")
    return data


def collapse(text):
    return " ".join(str(text).split())


def build_entry(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    fm = read_frontmatter(skill_md)
    slug = skill_dir.name

    entry = {
        "slug": slug,
        "name": str(fm.get("name", "")),
        "short_description": collapse(fm.get("description", "")),
        "source_path": f"skills/{slug}/SKILL.md",
    }

    meta = fm.get("metadata")
    if not isinstance(meta, dict):
        fail(f"{skill_md}: frontmatter must contain a 'metadata' mapping "
             f"(see CONTRIBUTING.md for the required keys)")
    unknown = set(meta) - set(METADATA_KEYS)
    if unknown:
        fail(f"{skill_md}: unknown metadata key(s): {', '.join(sorted(unknown))}")
    for src, dst in METADATA_KEYS.items():
        if src not in meta:
            fail(f"{skill_md}: metadata is missing required key '{src}'")
        value = meta[src]
        entry[dst] = collapse(value) if isinstance(value, str) else value

    if entry["name"] != slug:
        fail(f"{skill_md}: frontmatter name '{entry['name']}' must equal the "
             f"directory name '{slug}'")
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate only; do not write metadata.json")
    args = parser.parse_args()

    skill_dirs = sorted(
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    ) if SKILLS_DIR.is_dir() else []
    if not skill_dirs:
        fail("no skill directories (skills/<name>/SKILL.md) found")

    index = {
        "schema_version": "1",
        "repository": "webshare-proxy/skills",
        "skills": [build_entry(d) for d in skill_dirs],
    }

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(index, schema)
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        fail(f"schema validation failed at {path}: {e.message}")

    slugs = {s["slug"] for s in index["skills"]}
    for skill in index["skills"]:
        for related in skill["related_skills"]:
            if related not in slugs:
                fail(f"{skill['slug']}: related skill '{related}' does not "
                     f"exist in this catalog (have: {', '.join(sorted(slugs))})")
            if related == skill["slug"]:
                fail(f"{skill['slug']}: lists itself as a related skill")

    print(f"validated {len(index['skills'])} skills: "
          + ", ".join(sorted(slugs)))
    if not args.check:
        OUTPUT_PATH.write_text(json.dumps(index, indent=2) + "\n",
                               encoding="utf-8")
        print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
