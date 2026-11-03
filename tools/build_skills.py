#!/usr/bin/env python3
"""Regenerate Skills/reap-*/SKILL.md from README.md; --check validates sync."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reap_builder import ROOT, load_sections, render_skills


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "Skills")
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()
    generated = render_skills(load_sections())
    errors = []
    for rel_path, content in sorted(generated.items()):
        path = args.output_dir / rel_path
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                errors.append(rel_path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                path.write_text(content, encoding="utf-8", newline="\n")
    if errors:
        print("Out-of-date REAP skills:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"{'Validated' if args.check else 'Generated'} {len(generated)} REAP skill packs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())