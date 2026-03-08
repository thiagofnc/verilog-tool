"""Exports scan results to JSON."""

import json
from dataclasses import asdict
from pathlib import Path

try:
    from app.models import ScanResult
except ImportError:  # Supports running as: python app/main.py
    from models import ScanResult


def export_to_json(scan_result: ScanResult, output_path: str) -> Path:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(asdict(scan_result), indent=2), encoding="utf-8")
    return output_file
