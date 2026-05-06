# AGENTS.md

## Project
- **Purpose**: Linear programming solver (Simplex method + graphical method). Early stage.
- **Python**: 3.13, managed by **uv** (not pip/conda).
- **Entry point**: `main.py` (single-file app so far).

## Dependencies
- `fastapi[standard]` — web framework (backend planned).
- `matplotlib` — plotting for graphical method visualization.

## Commands
```bash
uv run main.py          # run the app
uv add <package>        # add dependency
uv sync                 # install/refresh deps from pyproject.toml
```

## Layout
- Single-file app currently. If `src/` or `tests/` appear, treat as new package boundaries.
- `.venv/` is the virtual env; never commit.

## Conventions
- Spanish domain terms in code (`restricciones`, `funcion_objetivo`, `metodoGrafico`). Follow this for LP domain naming.
- No lint/typecheck/test tooling configured yet. Do not assume ruff, mypy, or pytest.
