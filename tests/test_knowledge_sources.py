from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from knowledge_sources import collect_sources, validate_outputs
from privacy_check import fingerprint


class KnowledgeSourcesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def add(self, name, text, tracked=True):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if tracked:
            subprocess.run(["git", "-C", str(self.root), "add", "-f", name], check=True)
        return path

    def test_only_canonical_tracked_sources_are_selected(self):
        self.add("README.md", "# Brain")
        self.add(".claude/skills/content/SKILL.md", "# Content")
        self.add(".agents/skills/content/SKILL.md", "# Mirror")
        self.add("docs/private-draft.md", "Untracked draft", tracked=False)
        self.add("local/report.md", "Private report")
        self.add("config/company.local.json", "{}")
        self.add(".claude/skills/content/data/report.md", "Private data")
        self.assertEqual(set(collect_sources(self.root, set())), {"README.md", ".claude/skills/content/SKILL.md"})

    def test_symlink_is_rejected_without_reading_target(self):
        self.add("local/report.md", "Do not read")
        (self.root / "README.md").symlink_to("local/report.md")
        subprocess.run(["git", "-C", str(self.root), "add", "README.md"], check=True)
        with self.assertRaises(ValueError):
            collect_sources(self.root, set())

    def test_symlinked_parent_is_rejected(self):
        self.add("docs/guide.md", "# Guide")
        (self.root / "docs/guide.md").unlink()
        (self.root / "docs").rmdir()
        (self.root / "outside").mkdir()
        (self.root / "outside/guide.md").write_text("Private")
        (self.root / "docs").symlink_to("outside")
        with self.assertRaises(ValueError):
            collect_sources(self.root, set())

    def test_blocked_content_fails_without_echoing_it(self):
        self.add("README.md", "Synthetic restricted identifier")
        with self.assertRaises(ValueError) as error:
            collect_sources(self.root, {fingerprint("Synthetic restricted identifier")})
        self.assertNotIn("Synthetic restricted identifier", str(error.exception))

    def test_output_scan_catches_private_content(self):
        output = self.root / "graphify-out"
        output.mkdir()
        (output / "graph.json").write_text("Synthetic restricted identifier")
        with self.assertRaises(ValueError):
            validate_outputs(output, {fingerprint("Synthetic restricted identifier")})

    def test_clean_generated_output_is_allowed(self):
        output = self.root / "graphify-out"
        output.mkdir()
        (output / "graph.json").write_text('{"nodes": []}')
        validate_outputs(output, set())


if __name__ == "__main__":
    unittest.main()
