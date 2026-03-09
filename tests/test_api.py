import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    from fastapi.testclient import TestClient

    from app.api import app, state, state_lock
    from app.project_service import ProjectService
except Exception:  # pragma: no cover - dependency/setup guard
    TestClient = None


@unittest.skipUnless(TestClient is not None, "FastAPI test client is unavailable")
class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        with state_lock:
            state.service = ProjectService(parser_backend="simple")
            state.loaded_folder = None

    def test_requires_loaded_project_for_query_endpoints(self) -> None:
        response = self.client.get("/api/project/tops")
        self.assertEqual(response.status_code, 400)
        self.assertIn("No project loaded", response.json()["detail"])

    def test_project_load_and_graph_endpoints(self) -> None:
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

            load_response = self.client.post(
                "/api/project/load",
                json={"folder": str(root), "parser_backend": "simple"},
            )
            self.assertEqual(load_response.status_code, 200)
            summary = load_response.json()
            self.assertEqual(summary["file_count"], 2)
            self.assertEqual(summary["module_count"], 2)
            self.assertEqual(summary["top_candidates"], ["top"])

            project_response = self.client.get("/api/project")
            self.assertEqual(project_response.status_code, 200)
            self.assertIn("modules", project_response.json())

            tops_response = self.client.get("/api/project/tops")
            self.assertEqual(tops_response.status_code, 200)
            self.assertEqual(tops_response.json()["top_candidates"], ["top"])

            modules_response = self.client.get("/api/project/modules")
            self.assertEqual(modules_response.status_code, 200)
            self.assertEqual(modules_response.json()["modules"], ["child", "top"])

            module_response = self.client.get("/api/project/modules/top")
            self.assertEqual(module_response.status_code, 200)
            self.assertEqual(module_response.json()["name"], "top")

            graph_response = self.client.get("/api/project/graph/top")
            self.assertEqual(graph_response.status_code, 200)
            graph = graph_response.json()
            self.assertEqual(graph["schema_version"], "1.0")
            self.assertEqual(graph["top_module"], "top")

    def test_root_serves_ui_shell(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("RTL Architecture Visualizer", response.text)


if __name__ == "__main__":
    unittest.main()
