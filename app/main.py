"""CLI entry point for rtl_arch_visualizer."""

import argparse
from pathlib import Path

try:
    from app.json_exporter import export_to_json
    from app.scanner import scan_project
except ImportError:  # Supports running as: python app/main.py
    from json_exporter import export_to_json
    from scanner import scan_project


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rtl_arch_visualizer",
        description="Simple backend MVP that scans Verilog files and exports JSON.",
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Path to the Verilog project root (default: current directory).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="rtl_arch_output.json",
        help="Path for JSON output (default: rtl_arch_output.json).",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    result = scan_project(args.project_root)
    output_file = export_to_json(result, args.output)

    print(f"Scanned {len(result.files)} Verilog file(s).")
    print(f"Output written to: {Path(output_file).resolve()}")


if __name__ == "__main__":
    main()
