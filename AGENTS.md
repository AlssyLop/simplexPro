# AGENTS.md

## Project
- **Purpose**: Linear programming solver (Simplex method + graphical method).
- **Python**: 3.13, managed by **uv** (not pip/conda).
- **Entry point**: `main.py`.

## Dependencies
- `fastapi[standard]` — web framework.
- `matplotlib` — plotting.
- `aiosqlite` — async SQLite database operations.
- `fpdf2` — PDF report generation.

## Commands
```bash
uv run fastapi dev main.py  # Run development server
uv run main.py              # Execute script directly (if applicable)
uv add <package>
uv sync
```

## Conventions
- Spanish domain terms in code.
- Database: SQLite (`simplexPro.db`). Foreign keys must be explicitly enabled using `PRAGMA foreign_keys = ON`.
- Data persistence: Use `RETURNING` clause for atomic inserts/ID retrieval.
