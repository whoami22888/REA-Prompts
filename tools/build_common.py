"""Helpers for reproducible REAP Markdown generation."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SECTION = re.compile(r"^## (\d+)\. (.+)$", re.M)
SPECIAL = ("Wildcard prompt (start here)", "Prompt-writing tips (why these work)")


def source_sections():
    """Return ordered (title, Markdown content) from the canonical README."""
    text = README.read_text(encoding="utf-8")
    matches = list(SECTION.finditer(text))
    if len(matches) != 23 or [int(m.group(1)) for m in matches] != list(range(23)):
        raise ValueError("Expected consecutive README sections 0 through 22")
    starts = [(m.start(), m.group(0)[3:], m.end()) for m in matches]
    for heading in SPECIAL:
        match = re.search(r"^## " + re.escape(heading) + r"$", text, re.M)
        if match is None:
            raise ValueError(f"Missing README heading: {heading}")
        starts.append((match.start(), heading, match.end()))
    starts.sort()
    sections = []
    for i, (start, title, body_start) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        body = text[body_start:end].strip()
        # Ignore section-ending dividers, not dividers inside code fences.
        body = re.sub(r"\n---\s*$", "", body).strip()
        if title == SPECIAL[-1]:
            body = re.split(r"^## (?:Next steps:|License)\b", body, maxsplit=1, flags=re.M)[0].strip()
        sections.append((title, body))
    return sections


def section_slug(title):
    title = re.sub(r"^\d+\.\s*", "", title).lower().replace("&", "and")
    title = re.sub(r"[^a-z0-9]+", "-", title).strip("-")
    if title.startswith("wildcard-"):
        return "reap-wildcard"
    if title.startswith("prompt-writing-"):
        return "reap-prompt-writing-tips"
    numbered = re.match(r"^(\d+)\.\s", title)
    return "reap-" + title


def slug_for_section(title):
    num = re.match(r"^(\d+)\.\s*", title)
    if num:
        return f"reap-{int(num.group(1)):02d}-" + section_slug(title[len(num.group(0)):])[5:]
    return section_slug(title)


def prompt_count(body):
    return len(re.findall(r"^\x60\x60\x60text\s*$", body, re.M))
