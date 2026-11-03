import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_common import source_sections, slug_for_section, prompt_count
from build_skills import generate
from build_system_prompt import render


class BuildTests(unittest.TestCase):
    def test_inventory(self):
        sections = source_sections()
        self.assertEqual(len(sections), 25)
        self.assertEqual([int(t.split(".")[0]) for t, _ in sections[:23]], list(range(23)))
        self.assertEqual(len({slug_for_section(t) for t, _ in sections}), 25)
        self.assertEqual(sum(prompt_count(b) for _, b in sections), 104)

    def test_generation_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = generate(root)
            self.assertEqual(len(result), 25)
            before = {p.relative_to(root): p.read_bytes() for p in root.glob("reap-*/SKILL.md")}
            self.assertEqual(len(before), 26)
            self.assertIn(Path("reap-08-android/SKILL.md"), before)
            generate(root)
            after = {p.relative_to(root): p.read_bytes() for p in root.glob("reap-*/SKILL.md")}
            self.assertEqual(before, after)

    def test_system_prompt(self):
        content = render()
        self.assertEqual(content, render())
        self.assertEqual(content.count("\x60\x60\x60text"), 104)
        self.assertIn("## 8. Android", content)
        self.assertIn("## Wildcard prompt (start here)", content)

    def test_readme_case(self):
        self.assertTrue((Path(__file__).resolve().parents[1] / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
