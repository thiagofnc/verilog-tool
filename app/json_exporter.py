"""Export helpers for project scan results."""

import json
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any

try:
    from app.models import Project
except ImportError:  # Supports running as: python app/main.py
    from models import Project


def _to_plain_data(value: Any) -> Any:
    """Recursively convert dataclasses/lists/dicts into plain Python data."""
    if is_dataclass(value):
        return {field.name: _to_plain_data(getattr(value, field.name)) for field in fields(value)}

    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]

    if isinstance(value, dict):
        return {key: _to_plain_data(item) for key, item in value.items()}

    return value


def project_to_dict(project: Project) -> dict[str, Any]:
    """Convert a Project dataclass tree into a plain nested dictionary."""
    return _to_plain_data(project)


def save_project_json(project: Project, output_path: str) -> Path:
    """Save a Project model as formatted JSON and return the output path."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(project_to_dict(project), indent=2), encoding="utf-8")
    return output_file


def export_to_json(project: Project, output_path: str) -> Path:
    """Backward-compatible alias for previous exporter name."""
    return save_project_json(project, output_path)
