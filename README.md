# rtl_arch_visualizer

## Naming

Still deciding on the final project name: Verilogix, Silica, Verilium, Synthium, or ArchRTL.

Backend-only MVP for scanning and lightly parsing Verilog/SystemVerilog projects.

## Current MVP Capabilities

- Recursively scan a folder for visible `.v` and `.sv` files
- Skip hidden files and hidden folders
- Parse module definitions with either:
  - `pyverilog` backend (real AST parser)
  - `simple` backend (regex fallback)
- Extract:
  - module names
  - simple header ports (`input/output/inout`, optional width)
  - simple instances and basic named connections (`.port(signal)`)
- Infer likely top modules with simple testbench filtering
- Build and print a simple hierarchy tree when one top is inferred
- Build and print a simple nodes/edges hierarchy graph JSON
- Optionally export parsed project data to JSON

## Project Structure

- `app/main.py` - CLI entry point and console summary output
- `app/scanner.py` - file discovery and folder traversal
- `app/pyverilog_parser.py` - AST parser backend (PyVerilog)
- `app/simple_parser.py` - regex parser backend fallback
- `app/hierarchy.py` - top-module inference and hierarchy tree builder
- `app/graph_builder.py` - nodes/edges graph builder
- `app/parser_base.py` - parser backend interface
- `app/models.py` - dataclasses (`Project`, `ModuleDef`, etc.)
- `app/json_exporter.py` - dataclass-to-dict conversion and JSON save
- `tests/test_scanner.py` - scanner unit test
- `tests/test_simple_parser.py` - simple parser connection test
- `tests/test_graph_builder.py` - graph schema test
- `tests/test_pyverilog_parser.py` - PyVerilog parser backend test
- `out/` - primary exported project JSON (for CLI `--out`)
- `artifacts/summaries/` - saved text outputs from CLI tests
- `artifacts/debug/` - debug JSON outputs
- `artifacts/json/` - older/alternate JSON exports

## Requirements

- Python 3.10+
- For real parsing backend:

```bash
python -m pip install pyverilog
```

## How To Run

Replace `"C:\path\to\your\verilog-project"` with your own project folder path.

From the project root (default parser = `pyverilog`):

```bash
python -m app.main scan "C:\path\to\your\verilog-project"
```

Use regex fallback parser:

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser simple
```

With JSON output:

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser pyverilog --out out/project.json
```

With hierarchy graph JSON printed to console:

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser pyverilog --graph
```

## How To Test

Replace `"C:\path\to\your\verilog-project"` with your own project folder path.

1. Run unit tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

2. Run full flow on your project folder with PyVerilog:

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser pyverilog --graph --out out/project_pyverilog.json
```

3. Save summary output to artifacts:

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser pyverilog --graph --out out/project_pyverilog.json | Tee-Object -FilePath artifacts/summaries/pyverilog_scan_output.txt
```

## Notes and Limitations

- `pyverilog` is a stronger parser than regex, but this project still extracts a simplified model for MVP.
- Some advanced/SystemVerilog constructs may not parse cleanly yet.
- Top-module inference uses heuristics and may still need manual override in some projects.
