# rtl_arch_visualizer

Backend MVP for scanning and structurally analyzing Verilog/SystemVerilog projects, now with a service API and an interactive UI viewer shell.

## Naming

Still deciding on the final project name: Verilogix, Silica, Verilium, or ArchRTL.

## Project Goal

Build an executable, interactive architecture explorer that lets users choose a folder and navigate modules, submodules, ports, and signal connectivity with an EDA-style experience.

## Current Status (MVP)

- recursive Verilog/SystemVerilog file discovery (`.v`, `.sv`)
- parser backends: `pyverilog` (AST) and `simple` (regex fallback)
- normalized datamodel for modules/ports/signals/instances/pin mappings
- project service layer for reusable backend orchestration
- top-module inference + hierarchy tree builder
- stable graph schema (`module`, `instance`, `port`, `net`; `hierarchy`, `signal`)
- JSON export of parsed project model
- FastAPI backend endpoints
- graph viewer MVP in UI using Cytoscape.js
- hierarchy navigation with top list, tree navigation, and breadcrumb trail

## Architecture Flow

1. **Scanner** (`app/scanner.py`)
   - recursive walk
   - hidden file/folder filtering (dotfiles + Windows hidden attribute)
   - deterministic sorted output

2. **Parser** (`app/pyverilog_parser.py` or `app/simple_parser.py`)
   - extracts modules, ports, signals, instances
   - captures pin-level mappings (`child_port -> parent_signal`)

3. **Service Layer** (`app/project_service.py`)
   - `load_project(folder)`
   - `get_top_candidates()`
   - `get_hierarchy_tree(top_module)`
   - `get_module_graph(module_name)`
   - `get_project()`, `get_module()`, `get_module_names()`

4. **Hierarchy + Graph**
   - top inference + hierarchy tree (`app/hierarchy.py`)
   - stable graph build (`app/graph_builder.py`)

5. **Delivery**
   - CLI summary/output (`app/main.py`)
   - API endpoints + UI (`app/api.py`, `ui/`)

## Output Types

Project model JSON (`--out`):

- `root_path`
- `source_files`
- `modules`

Graph JSON (`--graph` or `/api/project/graph/{module}`):

- `schema_version`
- `top_module`
- `nodes` (`module`, `instance`, `port`, `net`)
- `edges` (`hierarchy`, `signal`)

## CLI Usage

From repo root, replace `C:\path\to\your\verilog-project` with your folder.

```bash
python -m app.main scan "C:\path\to\your\verilog-project"
```

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser pyverilog
python -m app.main scan "C:\path\to\your\verilog-project" --parser simple
```

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser pyverilog --out out/project.json
```

```bash
python -m app.main scan "C:\path\to\your\verilog-project" --parser pyverilog --graph
```

## API + UI Viewer

Install runtime dependencies:

```bash
python -m pip install fastapi uvicorn
```

Run server:

```bash
python -m uvicorn app.api:app --reload
```

Open UI:

- `http://127.0.0.1:8000/`

UI viewer features (steps 3 and 4):

- top toolbar for folder + parser selection
- hierarchy navigation panel with top candidates and tree view
- breadcrumb trail (`Top > Instance > Submodule` path)
- interactive Cytoscape graph viewer
- zoom/pan and fit-to-screen
- node selection and hover labels
- inspector panel for loaded-project and selected-node details

Current API endpoints:

- `GET /api/health`
- `POST /api/project/load`
- `GET /api/project`
- `GET /api/project/tops`
- `GET /api/project/modules`
- `GET /api/project/modules/{module_name}`
- `GET /api/project/hierarchy/{top_module}`
- `GET /api/project/graph/{module_name}`

## Testing

Run full test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Repository Layout

- `app/main.py` - CLI entry point
- `app/api.py` - FastAPI endpoints + UI serving
- `app/project_service.py` - backend orchestration API
- `app/scanner.py` - source discovery
- `app/models.py` - dataclasses
- `app/parser_base.py` - parser interface
- `app/pyverilog_parser.py` - AST parser backend
- `app/simple_parser.py` - regex parser backend
- `app/hierarchy.py` - top inference + hierarchy tree
- `app/graph_builder.py` - stable graph schema builder
- `app/json_exporter.py` - model JSON export
- `ui/` - viewer assets (`index.html`, `styles.css`, `app.js`)
- `tests/` - unit tests
- `out/` - generated model outputs
- `artifacts/` - scan summaries/debug artifacts

## Known Limitations

- not a full language elaborator yet
- some advanced SV constructs are not fully modeled
- top inference is heuristic
- graph layout is MVP-level and can be improved for very large designs
- Cytoscape is loaded from CDN in the current UI shell

## Generated Files

Do not commit generated parser/cache artifacts:

- `parsetab.py`
- `parser.out`
- `__pycache__/`

`.gitignore` includes these patterns.
