from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from publish_wiki import MARKER, sync_pages


class WikiSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.target = Path(self.temp.name) / "target"
        self.source.mkdir()
        self.target.mkdir()
        (self.source / "Brain-Home.md").write_text(MARKER + "\n# Brain\n")

    def test_updates_owned_pages_and_preserves_manual_pages(self):
        (self.target / "Home.md").write_text("My introduction")
        (self.target / "Notes.md").write_text("My notes")
        (self.target / "Brain-Old.md").write_text(MARKER + "\nOld")
        sync_pages(self.source, self.target)
        self.assertEqual((self.target / "Home.md").read_text(), "My introduction")
        self.assertEqual((self.target / "Notes.md").read_text(), "My notes")
        self.assertFalse((self.target / "Brain-Old.md").exists())
        self.assertTrue((self.target / "Brain-Home.md").exists())

    def test_name_collision_fails_before_deleting_or_writing(self):
        (self.target / "Brain-Home.md").write_text("Hand-written page")
        (self.target / "Brain-Old.md").write_text(MARKER + "\nOld")
        with self.assertRaises(ValueError):
            sync_pages(self.source, self.target)
        self.assertTrue((self.target / "Brain-Old.md").exists())
        self.assertEqual((self.target / "Brain-Home.md").read_text(), "Hand-written page")

    def test_rejects_unowned_input(self):
        (self.source / "Notes.md").write_text("Not generated")
        with self.assertRaises(ValueError):
            sync_pages(self.source, self.target)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_sidebar_preserves_manual_content_and_is_idempotent(self):
        (self.target / "_Sidebar.md").write_text("[My notes](Notes)\n")
        sync_pages(self.source, self.target)
        first = (self.target / "_Sidebar.md").read_text()
        sync_pages(self.source, self.target)
        self.assertEqual(first, (self.target / "_Sidebar.md").read_text())
        self.assertIn("[My notes](Notes)", first)
        self.assertIn("[Marketing Brain](Brain-Home)", first)

    def test_refuses_empty_source(self):
        (self.source / "Brain-Home.md").unlink()
        with self.assertRaises(ValueError):
            sync_pages(self.source, self.target)


if __name__ == "__main__":
    unittest.main()
