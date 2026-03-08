"""Simple directory scanner for Verilog source files."""

from pathlib import Path
from typing import Iterable

try:
    from app.models import ScanResult, VerilogFile
    from app.parser_base import NoOpParser, ParserBase
except ImportError:  # Supports running as: python app/main.py
    from models import ScanResult, VerilogFile
    from parser_base import NoOpParser, ParserBase

VERILOG_EXTENSIONS = (".v", ".sv", ".vh", ".svh")


def iter_verilog_files(project_root: Path) -> Iterable[Path]:
    for path in project_root.rglob("*"):
        if path.is_file() and path.suffix.lower() in VERILOG_EXTENSIONS:
            yield path


def scan_project(project_root: str, parser: ParserBase | None = None) -> ScanResult:
    root = Path(project_root).resolve()
    active_parser = parser or NoOpParser()

    result = ScanResult(project_root=str(root))
    for file_path in iter_verilog_files(root):
        modules = active_parser.parse_file(file_path)
        result.files.append(VerilogFile(path=str(file_path), modules=modules))

    return result
