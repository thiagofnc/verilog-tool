"""Very small regex-based Verilog parser backend for MVP use.

Assumptions / limitations:
- Targets simple Verilog/SystemVerilog module forms only.
- Expects module definitions to end with `endmodule`.
- Port extraction is based on module header text and may miss advanced syntax.
- Instance extraction supports basic `child_mod u1 (...);` style instantiations.
- Does not attempt to parse full language grammar.
"""

import os
import re
from pathlib import Path

try:
    from app.models import Instance, ModuleDef, Port, Project, SourceFile
    from app.parser_base import VerilogParserBackend
except ImportError:  # Supports running as: python app/main.py
    from models import Instance, ModuleDef, Port, Project, SourceFile
    from parser_base import VerilogParserBackend


MODULE_RE = re.compile(
    r"\bmodule\s+([A-Za-z_][A-Za-z0-9_$]*)"
    r"\s*(?:#\s*\(.*?\)\s*)?"
    r"(?:\((.*?)\))?\s*;"
    r"(.*?)"
    r"(?=\bendmodule\b)",
    flags=re.DOTALL,
)

INSTANCE_RE = re.compile(
    r"(?m)^\s*([A-Za-z_][A-Za-z0-9_$]*)\s+([A-Za-z_][A-Za-z0-9_$]*)\s*\((.*?)\)\s*;",
    flags=re.DOTALL,
)

NAMED_CONNECTION_RE = re.compile(
    r"\.\s*([A-Za-z_][A-Za-z0-9_$]*)\s*\(\s*([^()]*?)\s*\)"
)

KEYWORDS = {
    "if",
    "for",
    "while",
    "case",
    "assign",
    "always",
    "always_ff",
    "always_comb",
    "always_latch",
    "initial",
    "generate",
    "endgenerate",
}


def _remove_comments(text: str) -> str:
    """Drop line/block comments so regexes do not match comment text."""
    no_block = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", no_block)


def _parse_ports_from_header(header_text: str | None) -> list[Port]:
    """Parse simple module header ports such as `input clk, output [3:0] data`."""
    if not header_text:
        return []

    ports: list[Port] = []
    current_direction: str | None = None
    current_width: str | None = None

    for raw_part in header_text.split(","):
        part = " ".join(raw_part.split())
        if not part:
            continue

        direction_match = re.match(r"^(input|output|inout)\b", part)
        if direction_match:
            current_direction = direction_match.group(1)
            part = part[direction_match.end() :].strip()

        width_match = re.search(r"\[[^\]]+\]", part)
        if width_match:
            current_width = width_match.group(0)
            part = (part[: width_match.start()] + part[width_match.end() :]).strip()

        # Remove common net/type tokens; this parser is intentionally lightweight.
        part = re.sub(r"\b(wire|reg|logic|signed|unsigned|var)\b", "", part).strip()

        name_match = re.search(r"([A-Za-z_][A-Za-z0-9_$]*)$", part)
        if not name_match:
            continue

        ports.append(
            Port(
                name=name_match.group(1),
                direction=current_direction or "unknown",
                width=current_width,
            )
        )

    return ports


def _parse_connections(connection_text: str) -> dict[str, str]:
    """Parse named connections like `.a(sig)`; fallback to positional mapping."""
    named_matches = NAMED_CONNECTION_RE.findall(connection_text)
    if named_matches:
        return {port_name: signal.strip() for port_name, signal in named_matches}

    positional = [piece.strip() for piece in connection_text.split(",") if piece.strip()]
    return {f"arg{index}": signal for index, signal in enumerate(positional)}


def _parse_instances(module_body: str) -> list[Instance]:
    """Find basic instance declarations inside a module body."""
    instances: list[Instance] = []

    for module_name, inst_name, conn_text in INSTANCE_RE.findall(module_body):
        if module_name in KEYWORDS:
            continue

        instances.append(
            Instance(
                name=inst_name,
                module_name=module_name,
                connections=_parse_connections(conn_text),
            )
        )

    return instances


def _parse_modules_from_file(file_path: str) -> list[ModuleDef]:
    """Extract module definitions from a single file using regex matching."""
    text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    clean_text = _remove_comments(text)

    modules: list[ModuleDef] = []
    for module_name, header_text, body_text in MODULE_RE.findall(clean_text):
        modules.append(
            ModuleDef(
                name=module_name,
                ports=_parse_ports_from_header(header_text),
                instances=_parse_instances(body_text),
                source_file=str(Path(file_path).resolve()),
            )
        )

    return modules


class SimpleRegexParser(VerilogParserBackend):
    """Approximate parser backend for quick MVP extraction of modules/ports/instances."""

    def parse_files(self, file_paths: list[str]) -> Project:
        resolved_paths = [str(Path(path).resolve()) for path in file_paths]
        source_files = [SourceFile(path=path) for path in resolved_paths]

        modules: list[ModuleDef] = []
        for file_path in resolved_paths:
            if Path(file_path).suffix.lower() not in {".v", ".sv"}:
                continue
            modules.extend(_parse_modules_from_file(file_path))

        if resolved_paths:
            parent_dirs = [str(Path(path).parent) for path in resolved_paths]
            root_path = os.path.commonpath(parent_dirs)
        else:
            root_path = ""

        return Project(root_path=root_path, source_files=source_files, modules=modules)
