#!/usr/bin/env python3
"""Generate installable REAP skill packs from README.md (stdlib only)."""
import argparse
from pathlib import Path
from build_common import ROOT, source_sections, slug_for_section, prompt_count


def skill_document(slug, title, body):
    count = prompt_count(body)
    escaped = title.lower().replace('"', "'")
    return (
        "---\n"
        f"name: {slug}\n"
        f"description: REA prompt pack for {escaped}; {count} prompt templates.\n"
        "---\n\n"
        f"# REAP — {title}\n\n"
        "Part of REAP (REA Investigation Prompts). Work only within authorized scope. "
        "Investigate one feature at a time, start with static analysis, "
        "and cite file/function/address evidence.\n\n"
        f"{body}\n"
    )


def generate(output):
    sections = source_sections()
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for title, body in sections:
        slug = slug_for_section(title)
        count = prompt_count(body)
        target = output / slug / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(skill_document(slug, title, body), encoding="utf-8")
        rows.append((slug, title, count))
    index = [
        "---",
        "name: reap-prompts",
        "description: Master index for the REAP reverse-engineering agent skill packs.",
        "---",
        "",
        "# REAP — investigation skill index",
        "",
        "Only analyze software you own or are explicitly authorized to test. "
        "Load the corresponding skill for a single feature and cite evidence.",
        "",
        "| Skill | Section | Prompts |",
        "|---|---|---|",
    ]
    index += [f"| `{slug}` | {title} | {count} |" for slug, title, count in rows]
    index.append("")
    index_target = output / "reap-prompts" / "SKILL.md"
    index_target.parent.mkdir(parents=True, exist_ok=True)
    index_target.write_text("\n".join(index), encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "Skills")
    args = parser.parse_args()
    rows = generate(args.output)
    if len(rows) != 25 or len({r[0] for r in rows}) != 25:
        raise SystemExit("Invalid generated skill inventory")
    print(f"Generated {len(rows) + 1} skill packs in {args.output}")


if __name__ == "__main__":
    main()
