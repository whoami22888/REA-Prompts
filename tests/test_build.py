"""Deterministic REAP generation and Markdown/YAML regression checks."""
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from reap_builder import load_sections, parse_readme, render_skills, render_system_prompt  # noqa: E402


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sections = load_sections()
        cls.skills = render_skills(cls.sections)
        cls.prompt = render_system_prompt(cls.sections)

    def test_all_sections_and_skills_present(self) -> None:
        self.assertEqual([s.number for s in self.sections if s.number is not None], list(range(23)))
        self.assertEqual(len(self.skills), 26)
        self.assertEqual(len(set(self.skills)), 26)

    def test_source_prompts_preserved(self) -> None:
        source = [m.group(1) for s in self.sections for m in re.finditer(r"^```text\n(.*?)\n```", s.body, re.M | re.S)]
        output = [m.group(1) for m in re.finditer(r"^```text\n(.*?)\n```", self.prompt, re.M | re.S)]
        self.assertEqual(source, output)
        self.assertGreaterEqual(len(source), 100)

    def test_yaml_frontmatter_is_quoted_and_balanced(self) -> None:
        for path, content in self.skills.items():
            with self.subTest(path=path):
                self.assertRegex(content, r'^---\nname: reap-[\w-]+\ndescription: "[^\n]+"\n---\n')
                self.assertEqual(len(re.findall(r"^```", content, re.M)) % 2, 0)

    def test_generated_files_match_repository(self) -> None:
        for relative, expected in self.skills.items():
            with self.subTest(path=relative):
                self.assertEqual((ROOT / "Skills" / relative).read_text(encoding="utf-8"), expected)
        self.assertEqual((ROOT / "system_prompt.md").read_text(encoding="utf-8"), self.prompt)

    def test_deterministic_output(self) -> None:
        self.assertEqual(self.skills, render_skills(load_sections()))
        self.assertEqual(self.prompt, render_system_prompt(load_sections()))

    def test_corrupt_readme_fails_fast(self) -> None:
        with self.assertRaises(ValueError):
            parse_readme("## 0. Install & verify\nhello\n")


if __name__ == "__main__":
    unittest.main()