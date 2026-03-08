"""Helpers for inferring top modules and building a simple hierarchy tree."""

from pathlib import Path
from typing import Any

try:
    from app.models import ModuleDef
except ImportError:  # Supports running as: python app/main.py
    from models import ModuleDef


def _looks_like_testbench(module: ModuleDef) -> bool:
    """Heuristic filter for common testbench naming patterns."""
    lower_name = module.name.lower()
    file_name = Path(module.source_file).name.lower()

    return (
        lower_name.startswith("tb_")
        or lower_name.endswith("_tb")
        or lower_name.startswith("test_")
        or "testbench" in lower_name
        or file_name.startswith("tb_")
        or "testbench" in file_name
    )


def infer_top_modules(modules: list[ModuleDef], include_testbenches: bool = False) -> list[str]:
    """Return possible top modules based on instantiation graph and simple filtering."""
    module_lookup: dict[str, ModuleDef] = {}
    for module in modules:
        module_lookup.setdefault(module.name, module)

    module_names = set(module_lookup)
    instantiated_names: set[str] = set()

    for module in modules:
        for instance in module.instances:
            # Only count instantiated modules that are part of this parsed project.
            if instance.module_name in module_names:
                instantiated_names.add(instance.module_name)

    candidate_tops = sorted(module_names - instantiated_names)
    if include_testbenches:
        return candidate_tops

    filtered_tops = [
        module_name
        for module_name in candidate_tops
        if not _looks_like_testbench(module_lookup[module_name])
    ]

    # Fallback: if every candidate looks like a testbench, return original list.
    return filtered_tops or candidate_tops


def build_hierarchy_tree(modules: list[ModuleDef], top_module: str) -> dict[str, Any]:
    """Build a nested dictionary tree from a selected top module name."""
    module_lookup: dict[str, ModuleDef] = {}
    for module in modules:
        # Keep first definition if duplicates exist; good enough for MVP.
        module_lookup.setdefault(module.name, module)

    def build_node(module_name: str, active_path: set[str]) -> dict[str, Any]:
        node: dict[str, Any] = {"module": module_name, "instances": []}

        if module_name in active_path:
            # Break recursion on accidental cycles.
            node["cycle"] = True
            return node

        module_def = module_lookup.get(module_name)
        if module_def is None:
            node["unresolved"] = True
            return node

        next_path = set(active_path)
        next_path.add(module_name)

        children: list[dict[str, Any]] = []
        for instance in module_def.instances:
            child: dict[str, Any] = {
                "instance": instance.name,
                "module": instance.module_name,
            }

            if instance.module_name in module_lookup:
                child["children"] = build_node(instance.module_name, next_path)
            else:
                child["children"] = {
                    "module": instance.module_name,
                    "instances": [],
                    "unresolved": True,
                }

            children.append(child)

        node["instances"] = children
        return node

    return build_node(top_module, set())
