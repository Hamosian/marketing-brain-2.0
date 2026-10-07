import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from build_knowledge import document_graph, export_knowledge
from publish_wiki import MARKER


class KnowledgeBuildTests(unittest.TestCase):
    def test_explicit_links_skill_mentions_and_line_provenance(self):
        sources = {
            "README.md": "# Brain\n\n[Guide](docs/guide.md) and `content-agent`.\n",
            "docs/guide.md": "# Guide\n\n[Root](../README.md)\n",
            ".claude/skills/content-agent/SKILL.md": "---\nname: content-agent\n---\n# Content\n",
        }
        extraction = document_graph(sources)
        nodes = {node["id"]: node for node in extraction["nodes"]}
        edges = extraction["edges"]
        self.assertTrue(any(nodes[e["source"]].get("source_file") == "README.md" and nodes[e["target"]].get("source_file") == "docs/guide.md" for e in edges))
        self.assertTrue(any(e["relation"] == "mentions_skill" for e in edges))
        self.assertTrue(all(e["confidence"] == "EXTRACTED" and e["source_location"].startswith("L") for e in edges))

    def test_external_private_missing_and_code_fence_links_are_not_followed(self):
        sources = {"README.md": "# Brain\n[Private](local/report.md) [Outside](../../secret.md) [Web](https://example.com)\n```md\n[Example](docs/guide.md)\n```", "docs/guide.md": "# Guide"}
        extraction = document_graph(sources)
        self.assertFalse(any(e["relation"] == "references" for e in extraction["edges"]))

    def test_exports_graph_report_and_owned_wiki_with_valid_links(self):
        sources = {"README.md": "# Brain\n[Guide](docs/guide.md)", "docs/guide.md": "# Guide\n`README.md`", "scripts/helper.py": "def helper():\n    return True\n"}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result"
            export_knowledge(sources, output, "sample/brain", "a" * 40, set())
            data = json.loads((output / "graph.json").read_text())
            self.assertTrue(data["nodes"])
            code_nodes = [node for node in data["nodes"] if node.get("label") == "helper()"]
            self.assertTrue(code_nodes)
            self.assertTrue(all(node["source_file"] == "scripts/helper.py" for node in code_nodes))
            self.assertTrue((output / "graph.html").stat().st_size > 1000)
            self.assertIn("0", (output / "GRAPH_REPORT.md").read_text())
            pages = list((output / "wiki").glob("*.md"))
            self.assertTrue(pages)
            for page in pages:
                self.assertTrue(page.name.startswith("Brain-"))
                self.assertTrue(page.read_text().startswith(MARKER))
            self.assertTrue((output / "wiki/Brain-Home.md").exists())
            self.assertNotIn(directory, (output / "graph.json").read_text())


if __name__ == "__main__":
    unittest.main()
