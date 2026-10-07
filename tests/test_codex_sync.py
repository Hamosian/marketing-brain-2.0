import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("codex_sync", Path(__file__).resolve().parents[1] / "scripts/sync-codex.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class MirrorTests(unittest.TestCase):
    def test_check_detects_drift_without_writing_and_sync_preserves_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CLAUDE.md").write_text("See .claude/agents and .claude/skills")
            skill = root / ".claude/skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("Example skill")
            agent = root / ".claude/agents/example.md"
            agent.parent.mkdir(parents=True)
            agent.write_text("Example persona")
            sync.synchronize(root)
            self.assertEqual(sync.synchronize(root, check=True), [])
            mirror = root / ".agents/skills/example/SKILL.md"
            mirror.write_text("stale")
            self.assertTrue(sync.synchronize(root, check=True))
            self.assertEqual(mirror.read_text(), "stale")
            local = root / ".agents/skills/example/data/notes.md"
            local.parent.mkdir()
            local.write_text("Private runtime")
            skill.unlink()
            sync.synchronize(root)
            self.assertFalse(mirror.exists())
            self.assertEqual(local.read_text(), "Private runtime")
            self.assertEqual((root / ".agents/agents/example.md").read_text(), "Example persona")
            self.assertEqual(sync.synchronize(root, check=True), [])


if __name__ == "__main__":
    unittest.main()
