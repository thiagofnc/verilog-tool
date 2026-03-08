"""Base parser interfaces (no parsing implementation yet)."""

from abc import ABC, abstractmethod
from pathlib import Path


class ParserBase(ABC):
    @abstractmethod
    def parse_file(self, file_path: Path) -> list[str]:
        """Return parsed module names for a file."""
        raise NotImplementedError


class NoOpParser(ParserBase):
    def parse_file(self, file_path: Path) -> list[str]:
        """Placeholder parser used for the MVP scaffold."""
        return []
