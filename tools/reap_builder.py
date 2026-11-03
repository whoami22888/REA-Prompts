"""Build REAP agent prompts and skills from the canonical README.md.

No third-party dependencies. Neither parsing nor rendering executes prompt text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "README.md"
HEADINGS = re.compile(r"^## ([^\n]+)$", re.MULTILINE)
NUMBERED = re.compile(r"^(\d+)\. (.+)$")
SPECIAL = {"Wildcard prompt (start here)", "Prompt-writing tips (why these work)"}
INTRO = """You have access to the REAP prompt library: curated prompts for REA
(Reverse Engineer Anything, https://rea.tools/), for inspecting native
binaries, Go/Rust builds, web/Electron apps, games, firmware, Android,
kernels, APKs and malware.

Select the matching section for one specific feature. Replace placeholders
with concrete details. Check tool availability before claiming to use REA.
Start with static analysis, cite file/function/address evidence, distinguish
confirmed findings from inferences and unknowns, and end with a verifiable
deliverable. Only investigate software you own or have explicit authority to
test; limit sensitive research to defensive, educational and approved contexts."""


@dataclass(frozen=True)
class Section:
    heading: str
    body: str
    number: int | None

    @property
    def title(self) -> str:
        return self.heading.split(". ", 1)[1] if self.number is not None else self.heading

    @property
    def slug(self) -> str:
        if self.number is not None:
            return f"reap-{self.number:02d}-{slugify(self.title)}"
        if self.heading.startswith("Wildcard prompt"):
            return "reap-wildcard"
        return "reap-prompt-writing-tips"

    @property
    def count(self) -> int:
        return len(re.findall(r"^```text\s*$", self.body, re.MULTILINE))


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def parse_readme(text: str) -> list[Section]:
    """Extract the numbered skills and two supplemental sections, not README prose."""
    matches = list(HEADINGS.finditer(text))
    sections: list[Section] = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        numbered = NUMBERED.fullmatch(heading)
        if not numbered and heading not in SPECIAL:
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.end():end].strip()
        if not body:
            raise ValueError(f"Empty REAP section: {heading}")
        sections.append(Section(heading, body, int(numbered.group(1)) if numbered else None))
    numbers = [s.number for s in sections if s.number is not None]
    if numbers != list(range(23)):
        raise ValueError(f"Expected consecutive REAP sections 0..22; got {numbers}")
    specials = [s.heading for s in sections if s.number is None]
    if specials != ["Wildcard prompt (start here)", "Prompt-writing tips (why these work)"]:
        raise ValueError(f"Missing or out-of-order supplemental REAP sections: {specials}")
    return sections


def load_sections(source: Path = SOURCE) -> list[Section]:
    return parse_readme(source.read_text(encoding="utf-8"))


def frontmatter(name: str, description: str) -> str:
    # Quoted YAML is mandatory: unquoted values containing ': ' do not parse.
    return f"---\nname: {name}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n"


def skill_document(section: Section) -> str:
    label = section.title.split(" (", 1)[0] if section.number is None else section.title
    description = (
        f"REA prompt pack: {label} ({section.count} ready-to-paste prompts). "
        f"Use when doing reverse-engineering investigation of {label.lower()} "
        "with REA (rea.tools) via an AI coding agent."
    )
    preamble = (
        "Part of REAP (REA Investigation Prompts). Replace everything in "
        "<angle brackets>; keep each request focused on one feature. "
        "Demand file/function/address evidence and separate facts from hypotheses."
    )
    return (
        frontmatter(section.slug, description)
        + f"# REAP — {section.heading}\n\n{preamble}\n\n{section.body}\n"
    )


def index_document(sections: list[Section]) -> str:
    description = (
        "REAP master index: curated REA prompts for reverse engineering with AI "
        "coding agents (native binaries, Go/Rust source recovery, web/Electron, "
        "games, firmware, Android, kernel, malware, anti-cheat, protectors, cloning). "
        "Use when pointing an agent at RE work."
    )
    numbered = [s for s in sections if s.number is not None]
    wildcard, tips = sections[-2:]
    entries = numbered + [tips, wildcard]
    table = "\n".join(
        f"| `{s.slug}` | {s.heading.split(' (', 1)[0] if s.number is None else s.heading} | {s.count} |"
        for s in entries
    )
    return (
        frontmatter("reap-prompts", description)
        + "# REAP — REA Investigation Prompts (skill index)\n\n"
        + "A curated collection of prompts for [REA](https://rea.tools/). "
        + "Select the matching sibling skill folder, then adapt one prompt to the target.\n\n"
        + "> Only analyze owned or explicitly authorized software. Sensitive "
        + "research must stay within approved defensive, lab or CTF scope.\n\n"
        + "| Skill | Section | Prompts |\n|---|---|---|\n"
        + table
        + f"\n\n## {wildcard.heading}\n\n{wildcard.body}\n\n"
        + f"## {tips.heading}\n\n{tips.body}\n"
    )


def render_skills(sections: list[Section]) -> dict[str, str]:
    result = {f"{s.slug}/SKILL.md": skill_document(s) for s in sections}
    result["reap-prompts/SKILL.md"] = index_document(sections)
    if len(result) != 26:
        raise ValueError(f"Expected 26 unique skill packs, got {len(result)}")
    return result


def render_system_prompt(sections: list[Section]) -> str:
    blocks = [f"## {s.heading}\n{s.body}" for s in sections]
    return (
        "# REA Investigation Prompts (REAP) — system prompt\n\n"
        + INTRO.strip()
        + "\n\n"
        + "\n\n".join(blocks)
        + "\n"
    )