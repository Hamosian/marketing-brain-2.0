import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from company_config import EXAMPLE, initialize, validate
from privacy_check import POLICY, findings, fingerprint, scan


class CompanyConfigTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(EXAMPLE.read_text())

    def test_blank_template_valid_but_not_ready(self):
        self.assertEqual(validate(self.config), [])
        self.assertTrue(validate(self.config, require_ready=True))

    def test_valid_company_without_live_integrations(self):
        self.config["company"] = dict(name="Example Company", website="https://example.com", timezone="UTC", audiences=["Operations teams"], positioning="Synthetic test profile")
        self.assertEqual(validate(self.config, require_ready=True), [])

    def test_enabled_integration_needs_account(self):
        self.config["integrations"] = {"crm": {"enabled": True, "provider": "Example CRM"}}
        self.assertTrue(validate(self.config))

    def test_invalid_shapes_do_not_crash(self):
        for value in (None, [], "profile", 1, {"team": None}):
            with self.subTest(value=value):
                self.assertTrue(validate(value))

    def test_unsafe_or_invalid_configuration(self):
        for field, value in (("timezone", "Unknown/Zone"), ("website", "https://user:pass@example.com"), ("audiences", [None])):
            with self.subTest(field=field):
                config = json.loads(EXAMPLE.read_text())
                config["company"][field] = value
                self.assertTrue(validate(config))
        self.config["automation"]["enabled"] = True
        self.assertTrue(validate(self.config))

    def test_initialization_preserves_existing_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "company.local.json"
            initialize(EXAMPLE, target)
            target.write_text("private existing profile")
            with self.assertRaises(FileExistsError):
                initialize(EXAMPLE, target)
            self.assertEqual(target.read_text(), "private existing profile")


class PrivacyTests(unittest.TestCase):
    def test_normalized_names_and_paths(self):
        blocked = {fingerprint("Example Former Employer"), fingerprint("Example Person")}
        self.assertTrue(findings("docs/note.md", b"EXAMPLE\nFormer Employer", blocked))
        self.assertTrue(findings("reports/example-person.md", b"", blocked))
        self.assertEqual(findings("docs/guide.md", b"Reusable instructions", blocked), [])

    def test_private_content_and_paths(self):
        self.assertTrue(findings("config/company.local.json", b"{}", set()))
        self.assertTrue(findings(".claude/skills/brief/data/notes.md", b"notes", set()))
        self.assertTrue(findings("report.pptx", b"\x00\xff", set()))
        url = "https://docs.google.com/document/d/" + "A" * 30
        self.assertTrue(findings("notes.md", url.encode(), set()))
        token = "gh" + "p_" + "A" * 40
        self.assertTrue(findings("notes.md", token.encode(), set()))

    def test_staged_mode_checks_index_not_clean_worktree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            policy = root / POLICY
            policy.parent.mkdir()
            policy.write_text(json.dumps({"sha256": [fingerprint("Example Former Employer")]}))
            note = root / "note.md"
            note.write_text("Example Former Employer")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            note.write_text("Clean working copy")
            self.assertEqual(len(scan(root, staged=True)[1]), 1)
            self.assertEqual(scan(root)[1], [])

    def test_binary_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            policy = root / POLICY
            policy.parent.mkdir()
            policy.write_text(json.dumps({"sha256": [fingerprint("Synthetic blocked identifier")]}))
            (root / "unreviewed.bin").write_bytes(b"\xff")
            (root / "link.md").symlink_to(policy)
            self.assertEqual(len(scan(root)[1]), 2)


if __name__ == "__main__":
    unittest.main()
