import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.project_service import ProjectService


class TestProjectService(unittest.TestCase):
    def test_load_project_top_candidates_and_module_graph(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            (root / "child.v").write_text(
                """
module child(input clk);
endmodule
""".strip()
                + "\n",
                encoding="utf-8",
            )

            (root / "top.v").write_text(
                """
module top(input clk);
  wire local_net;
  child u1 (
    .clk(clk)
  );
endmodule
""".strip()
                + "\n",
                encoding="utf-8",
            )

            service = ProjectService(parser_backend="simple")
            project = service.load_project(str(root))

            self.assertEqual(len(project.source_files), 2)

            top_candidates = service.get_top_candidates()
            self.assertEqual(top_candidates, ["top"])

            graph = service.get_module_graph("top")
            self.assertEqual(graph["schema_version"], "1.0")
            self.assertEqual(graph["top_module"], "top")

            node_ids = {node["id"] for node in graph["nodes"]}
            edge_tuples = {(edge["source"], edge["target"], edge["kind"]) for edge in graph["edges"]}

            self.assertIn("module:top", node_ids)
            self.assertIn("instance:top/u1", node_ids)
            self.assertIn("port:instance:top/u1:clk", node_ids)

            self.assertIn(("module:top", "instance:top/u1", "hierarchy"), edge_tuples)
            self.assertIn(("net:top:clk", "port:instance:top/u1:clk", "signal"), edge_tuples)

            with self.assertRaises(ValueError):
                service.get_module_graph("missing_module")

    def test_requires_project_to_be_loaded(self) -> None:
        service = ProjectService(parser_backend="simple")

        with self.assertRaises(RuntimeError):
            service.get_top_candidates()

        with self.assertRaises(RuntimeError):
            service.get_module_graph("top")


if __name__ == "__main__":
    unittest.main()
