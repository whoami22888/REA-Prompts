#!/usr/bin/env python3
"""Regenerate system_prompt.md from README.md; --check validates sync."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reap_builder import ROOT, load_sections, render_system_prompt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "system_prompt.md")
    parser.add_argument("--check", action="store_true", help="fail if generated file differs")
    args = parser.parse_args()
    generated = render_system_prompt(load_sections())
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != generated:
            print(f"Out-of-date REAP prompt: {args.output}", file=sys.stderr)
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != generated:
            args.output.write_text(generated, encoding="utf-8", newline="\n")
    print(f"{'Validated' if args.check else 'Generated'} REAP system prompt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())