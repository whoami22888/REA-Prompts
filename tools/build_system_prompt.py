#!/usr/bin/env python3
"""Rebuild one agent-ready system prompt from README.md (stdlib only)."""
import argparse
from pathlib import Path
from build_common import ROOT, source_sections


def render():
    sections = source_sections()
    intro = (
        "# REA Investigation Prompts (REAP) — system prompt\n\n"
        "Use REA (https://rea.tools/) only when it is actually available. "
        "Only analyze software that you own or are expressly authorized to assess. "
        "Choose one feature and the relevant section below. "
        "Begin with static analysis; cite file/function/address evidence. "
        "Separate confirmed facts, inferences, and unknowns. "
        "For protection, anti-cheat, DMA, malware and vulnerability studies, "
        "remain within defensive, permitted research or lab work. "
        "End with a reproducible deliverable and actual verification results.\n"
    )
    return intro + "".join(
        f"\n---\n\n## {title}\n\n{body}\n" for title, body in sections
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "system_prompt.md")
    args = parser.parse_args()
    content = render()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
