# rtl_arch_visualizer

A very simple backend-only MVP scaffold for analyzing Verilog projects.

## Project Structure

- `app/main.py` - CLI entry point
- `app/scanner.py` - recursively finds Verilog files
- `app/models.py` - lightweight dataclasses for scan output
- `app/parser_base.py` - parser interface + no-op parser
- `app/json_exporter.py` - writes scan results to JSON
- `tests/` - placeholder test directory

## Run Locally

1. Use Python 3.10+.
2. From this project root, run:

```bash
python app/main.py . -o rtl_arch_output.json
```

Or run as module:

```bash
python -m app.main . -o rtl_arch_output.json
```

3. Check `rtl_arch_output.json` for output.
