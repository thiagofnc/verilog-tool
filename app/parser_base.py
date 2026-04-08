"""Base parser backend interface (no real parser implementation yet)."""

from abc import ABC, abstractmethod
from typing import Callable, Optional

try:
    from app.models import Project
except ImportError:  # Supports running as: python app/main.py
    from models import Project


# Callback signature: (current_file_index, total_files, current_file_path)
ProgressCallback = Callable[[int, int, str], None]


class VerilogParserBackend(ABC):
    """Abstract interface for pluggable Verilog parser backends."""

    @abstractmethod
    def parse_files(
        self,
        file_paths: list[str],
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Project:
        """Parse the provided Verilog file paths and return a Project model."""
        raise NotImplementedError


class DummyParser(VerilogParserBackend):
    """Placeholder backend used until a real parser is implemented."""

    def parse_files(
        self,
        file_paths: list[str],
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Project:
        raise NotImplementedError("DummyParser does not implement parsing yet.")
