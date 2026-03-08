"""Simple data models for scanner output."""

from dataclasses import dataclass, field


@dataclass
class VerilogFile:
    path: str
    modules: list[str] = field(default_factory=list)


@dataclass
class ScanResult:
    project_root: str
    files: list[VerilogFile] = field(default_factory=list)
