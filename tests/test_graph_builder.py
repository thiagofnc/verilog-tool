import unittest

from app.graph_builder import build_hierarchy_graph, build_module_connectivity_graph
from app.models import Instance, ModuleDef, PinConnection, Port, Project, Signal, SourceFile


class TestGraphBuilder(unittest.TestCase):
    def _build_project(self) -> Project:
        return Project(
            root_path=".",
            source_files=[SourceFile(path="top.v"), SourceFile(path="child.v")],
            modules=[
                ModuleDef(
                    name="top",
                    ports=[Port(name="clk", direction="input"), Port(name="y", direction="output")],
                    signals=[Signal(name="sig_a", kind="wire")],
                    instances=[
                        Instance(
                            name="u1",
                            module_name="child",
                            connections={"a": "sig_a", "clk": "clk", "y": "y"},
                            pin_connections=[
                                PinConnection(child_port="a", parent_signal="sig_a"),
                                PinConnection(child_port="clk", parent_signal="clk"),
                                PinConnection(child_port="y", parent_signal="y"),
                            ],
                        )
                    ],
                    source_file="top.v",
                ),
                ModuleDef(
                    name="child",
                    ports=[
                        Port(name="a", direction="input"),
                        Port(name="clk", direction="input"),
                        Port(name="y", direction="output"),
                    ],
                    instances=[],
                    source_file="child.v",
                ),
            ],
        )

    def test_builds_stable_hierarchy_schema(self) -> None:
        project = self._build_project()
        graph = build_hierarchy_graph(project, "top")

        self.assertEqual(graph["schema_version"], "1.0")
        self.assertEqual(graph["top_module"], "top")

        node_ids = {node["id"] for node in graph["nodes"]}
        edge_tuples = {(edge["source"], edge["target"], edge["kind"]) for edge in graph["edges"]}

        self.assertIn("module:top", node_ids)
        self.assertIn("instance:top/u1", node_ids)
        self.assertIn(("module:top", "instance:top/u1", "hierarchy"), edge_tuples)

    def test_builds_compact_module_connectivity_graph(self) -> None:
        project = self._build_project()
        graph = build_module_connectivity_graph(project, "top", mode="compact")

        self.assertEqual(graph["schema_version"], "1.0-connectivity")
        self.assertEqual(graph["focus_module"], "top")
        self.assertEqual(graph["mode"], "compact")

        node_ids = {node["id"] for node in graph["nodes"]}
        edge_kinds = {edge["kind"] for edge in graph["edges"]}

        self.assertIn("instance:u1", node_ids)
        self.assertIn("io:clk", node_ids)
        self.assertIn("io:y", node_ids)
        self.assertEqual(edge_kinds, {"connection"})

        # Expect directed wiring from module input to child input on shared signal.
        self.assertTrue(
            any(
                edge["source"] == "io:clk"
                and edge["target"] == "instance:u1"
                and edge["net"] == "clk"
                for edge in graph["edges"]
            )
        )

        # Expect directed wiring from child output back to module output on shared signal.
        self.assertTrue(
            any(
                edge["source"] == "instance:u1"
                and edge["target"] == "io:y"
                and edge["net"] == "y"
                for edge in graph["edges"]
            )
        )


if __name__ == "__main__":
    unittest.main()
