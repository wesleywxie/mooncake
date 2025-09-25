# Repository Guidelines

## Project Structure & Module Organization
- Source: `app/` (config, DB helpers, services, models)
- Entrypoints: `main.py` (smoke scrape), `examples/save_movies.py` (persist to DB)
- Tests: `tests/` (unittest), mirrors app structure (e.g., `tests/services/`)
- Assets/Data: SQLite default at `mooncake.db` unless `DATABASE_URL` is set

## Build, Test, and Development Commands
- Create venv and install deps:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
- Set module path for absolute imports:
  - `export PYTHONPATH=$(pwd)/app`
- Run locally (prints parsed details):
  - `python main.py`
- Persist scraped data to DB:
  - `python examples/save_movies.py`
- Run tests:
  - `python -m unittest discover tests`

## Coding Style & Naming Conventions
- Python 3.12+, PEP 8, 4-space indentation
- Prefer type hints with built-in generics (e.g., `list[str]`, `dict[str, Any]`)
- Modules and packages: `snake_case`; classes: `PascalCase`; functions/vars: `snake_case`
- Keep services cohesive in `app/services/` and ORM models in `app/models/`
- Logging follows `app.config.Config` settings (`LOGGING_LEVEL`, `LOGGING_FORMAT`)

## Testing Guidelines
- Framework: `unittest`; name tests `test_*.py` under `tests/`
- Hermetic tests: mock network (`WaterCrawlAPIClient`) and use in-memory SQLite (`sqlite+pysqlite:///:memory:`)
- Example discovery:
  - `python -m unittest discover tests`
- Target edge cases (missing HTML nodes, parsing fallbacks, idempotent upserts)

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, etc.
- PRs should include:
  - Clear description and linked issues
  - Test updates and passing CI
  - Logs/screenshots for scraping changes when applicable
  - Config updates reflected in `.env.example`

## Security & Configuration Tips
- Do not commit secrets. Use `.env` locally; env vars override `.env`.
- Required config: `WATER_CRAWL_BASE_URL`, `WATER_CRAWL_API_KEY`; optional: `DATABASE_URL`, `DEBUG`.
- Default DB is SQLite (`sqlite:///mooncake.db`); prefer Postgres for multi-user setups.

