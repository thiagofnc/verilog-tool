"""Graph builders for hierarchy and module-internal connectivity views."""

from collections import defaultdict
from typing import Any

try:
    from app.models import Instance, ModuleDef, Project
except ImportError:  # Supports running as: python app/main.py
    from models import Instance, ModuleDef, Project


GRAPH_SCHEMA_VERSION = "1.0"
CONNECTIVITY_SCHEMA_VERSION = "1.0-connectivity"


def _build_module_lookup(modules: list[ModuleDef]) -> dict[str, ModuleDef]:
    lookup: dict[str, ModuleDef] = {}
    for module in modules:
        # Keep first definition if duplicates exist.
        lookup.setdefault(module.name, module)
    return lookup


def _port_direction(module_def: ModuleDef, port_name: str) -> str:
    for port in module_def.ports:
        if port.name == port_name:
            return (port.direction or "unknown").lower()
    return "unknown"


def _endpoint_role(direction: str) -> str:
    normalized = direction.lower()
    if normalized == "output":
        return "source"
    if normalized == "input":
        return "sink"
    if normalized == "inout":
        return "bidir"
    return "unknown"


def _endpoint_flow_role(endpoint: dict[str, Any]) -> str:
    """Map endpoint direction to signal flow role in the viewed module scope.

    Instance pin directions are interpreted as written on the child module.
    Module I/O directions are interpreted from inside the current module.
    """
    role = _endpoint_role(endpoint["direction"])
    if endpoint.get("endpoint_kind") != "module_io":
        return role

    # Module input pins feed logic in this scope, while module outputs consume it.
    if role == "source":
        return "sink"
    if role == "sink":
        return "source"
    return role


def _instance_pin_pairs(instance: Instance) -> list[tuple[str, str]]:
    if instance.pin_connections:
        pairs = [(pin.child_port, pin.parent_signal) for pin in instance.pin_connections]
    else:
        pairs = list(instance.connections.items())

    cleaned: list[tuple[str, str]] = []
    for child_port, parent_signal in pairs:
        signal = " ".join(parent_signal.split())
        if not signal:
            signal = f"__open__:{instance.name}.{child_port}"
        cleaned.append((child_port, signal))

    return cleaned


def _aggregate_compact_edges(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse parallel compact edges by source/target/flow for cleaner layouts."""
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}

    for edge in edges:
        key = (edge["source"], edge["target"], edge.get("flow", "directed"))
        group = grouped.get(key)
        if group is None:
            group = {
                "source": edge["source"],
                "target": edge["target"],
                "kind": edge.get("kind", "connection"),
                "flow": edge.get("flow", "directed"),
                "nets": [],
                "connections": [],
            }
            grouped[key] = group

        net_name = edge.get("net", "")
        if net_name and net_name not in group["nets"]:
            group["nets"].append(net_name)

        group["connections"].append(
            {
                "net": net_name,
                "source_port": edge.get("source_port", ""),
                "target_port": edge.get("target_port", ""),
            }
        )

    aggregated: list[dict[str, Any]] = []
    for group in grouped.values():
        group["net_count"] = len(group["nets"])
        if group["net_count"] == 1:
            group["net"] = group["nets"][0]
        aggregated.append(group)

    aggregated.sort(key=lambda edge: (edge["source"], edge["target"], edge.get("flow", "")))
    return aggregated


def build_module_connectivity_graph(
    project: Project,
    module_name: str,
    mode: str = "compact",
    aggregate_edges: bool = False,
) -> dict[str, Any]:
    """Build a module-scope connectivity graph from shared parent signals.

    Mode:
    - compact: instance/module-io nodes + direct connection edges with net metadata.
    - detailed: adds net nodes and routes connections through nets.
    """
    if mode not in {"compact", "detailed"}:
        raise ValueError("Unsupported connectivity mode. Use 'compact' or 'detailed'.")

    module_lookup = _build_module_lookup(project.modules)
    module_def = module_lookup.get(module_name)
    if module_def is None:
        raise ValueError(f"Module not found in project: {module_name}")

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_node_ids: set[str] = set()
    seen_edges: set[tuple[Any, ...]] = set()

    def add_node(node: dict[str, Any]) -> None:
        node_id = str(node["id"])
        if node_id in seen_node_ids:
            return
        seen_node_ids.add(node_id)
        nodes.append(node)

    def add_edge(edge: dict[str, Any]) -> None:
        key = (
            edge["source"],
            edge["target"],
            edge.get("kind", "connection"),
            edge.get("net", ""),
            edge.get("source_port", ""),
            edge.get("target_port", ""),
            edge.get("flow", ""),
        )
        if key in seen_edges:
            return
        seen_edges.add(key)
        edges.append(edge)

    attachments_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)

    # Module I/O as first-class endpoints in this module-scope connectivity view.
    for port in sorted(module_def.ports, key=lambda p: p.name):
        node_id = f"io:{port.name}"
        add_node(
            {
                "id": node_id,
                "label": f"{port.name} ({port.direction})",
                "kind": "module_io",
                "port_name": port.name,
                "direction": (port.direction or "unknown").lower(),
            }
        )
        attachments_by_signal[port.name].append(
            {
                "node_id": node_id,
                "endpoint_kind": "module_io",
                "port_name": port.name,
                "direction": (port.direction or "unknown").lower(),
            }
        )

    # Instance-level endpoints attached to parent-module signals.
    for instance in sorted(module_def.instances, key=lambda i: i.name):
        instance_id = f"instance:{instance.name}"
        add_node(
            {
                "id": instance_id,
                "label": f"{instance.name}: {instance.module_name}",
                "kind": "instance",
                "instance_name": instance.name,
                "module_name": instance.module_name,
            }
        )

        child_module_def = module_lookup.get(instance.module_name)

        for child_port, parent_signal in _instance_pin_pairs(instance):
            direction = "unknown"
            if child_module_def is not None:
                direction = _port_direction(child_module_def, child_port)

            attachments_by_signal[parent_signal].append(
                {
                    "node_id": instance_id,
                    "endpoint_kind": "instance_pin",
                    "instance_name": instance.name,
                    "module_name": instance.module_name,
                    "port_name": child_port,
                    "direction": direction,
                }
            )

    if mode == "detailed":
        for signal_name in sorted(attachments_by_signal):
            net_id = f"net:{signal_name}"
            add_node(
                {
                    "id": net_id,
                    "label": signal_name,
                    "kind": "net",
                    "signal_name": signal_name,
                }
            )

            for endpoint in attachments_by_signal[signal_name]:
                role = _endpoint_flow_role(endpoint)

                if role in {"source", "bidir"}:
                    add_edge(
                        {
                            "source": endpoint["node_id"],
                            "target": net_id,
                            "kind": "connection",
                            "net": signal_name,
                            "source_port": endpoint["port_name"],
                            "target_port": signal_name,
                            "flow": "directed",
                        }
                    )

                if role in {"sink", "bidir"}:
                    add_edge(
                        {
                            "source": net_id,
                            "target": endpoint["node_id"],
                            "kind": "connection",
                            "net": signal_name,
                            "source_port": signal_name,
                            "target_port": endpoint["port_name"],
                            "flow": "directed",
                        }
                    )

                if role == "unknown":
                    add_edge(
                        {
                            "source": net_id,
                            "target": endpoint["node_id"],
                            "kind": "connection",
                            "net": signal_name,
                            "source_port": signal_name,
                            "target_port": endpoint["port_name"],
                            "flow": "unknown",
                        }
                    )

    else:
        for signal_name in sorted(attachments_by_signal):
            endpoints = attachments_by_signal[signal_name]
            sources = [ep for ep in endpoints if _endpoint_flow_role(ep) in {"source", "bidir"}]
            sinks = [ep for ep in endpoints if _endpoint_flow_role(ep) in {"sink", "bidir"}]

            if sources and sinks:
                for source in sources:
                    for sink in sinks:
                        if source["node_id"] == sink["node_id"]:
                            continue

                        add_edge(
                            {
                                "source": source["node_id"],
                                "target": sink["node_id"],
                                "kind": "connection",
                                "net": signal_name,
                                "source_port": source["port_name"],
                                "target_port": sink["port_name"],
                                "flow": "directed",
                            }
                        )
            else:
                # Unknown directionality fallback keeps connectivity visible.
                ordered = sorted(endpoints, key=lambda ep: (ep["node_id"], ep.get("port_name", "")))
                for index, left in enumerate(ordered):
                    for right in ordered[index + 1 :]:
                        if left["node_id"] == right["node_id"]:
                            continue

                        add_edge(
                            {
                                "source": left["node_id"],
                                "target": right["node_id"],
                                "kind": "connection",
                                "net": signal_name,
                                "source_port": left["port_name"],
                                "target_port": right["port_name"],
                                "flow": "unknown",
                            }
                        )

    return {
        "schema_version": CONNECTIVITY_SCHEMA_VERSION,
        "view": "module_connectivity",
        "mode": mode,
        "top_module": module_name,
        "focus_module": module_name,
        "nodes": nodes,
        "edges": _aggregate_compact_edges(edges) if mode == "compact" and aggregate_edges else edges,
    }


def build_hierarchy_graph(project: Project, top_module: str) -> dict[str, Any]:
    """Build a stable graph schema with module/instance/port/net nodes.

    Node shape: {id, label, kind}
    Edge shape: {source, target, kind}

    Edge kinds:
    - hierarchy: ownership/structure links (module->instance, module->port, etc.)
    - signal: wiring links (net->port, port->net)
    """
    module_lookup = _build_module_lookup(project.modules)

    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []
    seen_node_ids: set[str] = set()
    seen_edges: set[tuple[str, str, str]] = set()

    def add_node(node_id: str, label: str, kind: str) -> None:
        if node_id in seen_node_ids:
            return
        seen_node_ids.add(node_id)
        nodes.append({"id": node_id, "label": label, "kind": kind})

    def add_edge(source: str, target: str, kind: str) -> None:
        key = (source, target, kind)
        if key in seen_edges:
            return
        seen_edges.add(key)
        edges.append({"source": source, "target": target, "kind": kind})

    def module_node_id(path_id: str) -> str:
        return f"module:{path_id}"

    def instance_node_id(parent_path_id: str, instance_name: str) -> str:
        return f"instance:{parent_path_id}/{instance_name}"

    def module_port_node_id(module_path_id: str, port_name: str) -> str:
        return f"port:{module_path_id}:{port_name}"

    def instance_port_node_id(instance_id: str, port_name: str) -> str:
        return f"port:{instance_id}:{port_name}"

    def net_node_id(module_path_id: str, signal_name: str) -> str:
        return f"net:{module_path_id}:{signal_name}"

    def add_module_interface_nodes(module_def: ModuleDef, module_id: str, module_path_id: str) -> set[str]:
        # Track names that exist as nets in this module scope.
        known_nets: set[str] = set()

        for port in sorted(module_def.ports, key=lambda p: p.name):
            port_id = module_port_node_id(module_path_id, port.name)
            add_node(port_id, f"{port.name} ({port.direction})", "port")
            add_edge(module_id, port_id, "hierarchy")

            # Treat interface names as addressable nets for parent/child wiring.
            net_id = net_node_id(module_path_id, port.name)
            add_node(net_id, port.name, "net")
            add_edge(port_id, net_id, "signal")
            known_nets.add(port.name)

        for signal in sorted(module_def.signals, key=lambda s: s.name):
            net_id = net_node_id(module_path_id, signal.name)
            add_node(net_id, signal.name, "net")
            add_edge(module_id, net_id, "hierarchy")
            known_nets.add(signal.name)

        return known_nets

    def connect_instance_pins(
        module_path_id: str,
        instance: Instance,
        instance_id: str,
        known_nets: set[str],
    ) -> None:
        if instance.pin_connections:
            pin_pairs = sorted(
                ((pin.child_port, pin.parent_signal) for pin in instance.pin_connections),
                key=lambda pair: pair[0],
            )
        else:
            pin_pairs = sorted(instance.connections.items(), key=lambda pair: pair[0])

        for child_port, parent_signal in pin_pairs:
            signal_name = parent_signal.strip()
            if not signal_name:
                # Preserve open/unconnected pins without generating empty net ids.
                signal_name = f"__open__:{instance.name}.{child_port}"

            pin_id = instance_port_node_id(instance_id, child_port)
            add_node(pin_id, f"{instance.name}.{child_port}", "port")
            add_edge(instance_id, pin_id, "hierarchy")

            if signal_name not in known_nets:
                # Connections may reference names that were not explicitly declared
                # (for example, implicit nets or parser-limited cases).
                implicit_net_id = net_node_id(module_path_id, signal_name)
                add_node(implicit_net_id, signal_name, "net")
                add_edge(module_node_id(module_path_id), implicit_net_id, "hierarchy")
                known_nets.add(signal_name)

            add_edge(net_node_id(module_path_id, signal_name), pin_id, "signal")

    def walk(module_name: str, module_path_id: str, active_modules: set[str]) -> None:
        module_def = module_lookup.get(module_name)
        module_id = module_node_id(module_path_id)
        add_node(module_id, module_name, "module")

        if module_def is None:
            return

        known_nets = add_module_interface_nodes(module_def, module_id, module_path_id)

        if module_name in active_modules:
            return

        next_active = set(active_modules)
        next_active.add(module_name)

        for instance in sorted(module_def.instances, key=lambda i: i.name):
            inst_id = instance_node_id(module_path_id, instance.name)
            add_node(inst_id, f"{instance.name}: {instance.module_name}", "instance")
            add_edge(module_id, inst_id, "hierarchy")

            connect_instance_pins(module_path_id, instance, inst_id, known_nets)

            child_path_id = f"{module_path_id}/{instance.name}:{instance.module_name}"
            child_module_id = module_node_id(child_path_id)
            add_node(child_module_id, instance.module_name, "module")
            add_edge(inst_id, child_module_id, "hierarchy")

            if instance.module_name in module_lookup:
                walk(instance.module_name, child_path_id, next_active)

    walk(top_module, top_module, set())

    return {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "top_module": top_module,
        "nodes": nodes,
        "edges": edges,
    }
