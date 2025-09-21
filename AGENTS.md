# Repository Guidelines

## Project Structure & Modules
- app/: application code
  - config.py, ext.py, models/, services/
- tests/: unit tests mirroring app layout
- main.py: example runner/smoke script
- requirements.txt: Python dependencies
- .env, .env.example: runtime configuration

Imports assume PYTHONPATH includes app. Examples:
- from models.movie import MovieListItem
- from app.services.water_crawler import WaterCrawler

## Build, Test, and Development
- Create env and install:
  - python -m venv .venv && source .venv/bin/activate
  - pip install -r requirements.txt
- Set module path (shell): export PYTHONPATH=$(pwd)/app
- Run locally (requires WATER_CRAWL_*): python main.py
- Run tests: python -m unittest discover tests
- Coverage (local):
  - pip install coverage
  - coverage run -m unittest discover tests && coverage report

## Coding Style & Naming
- Python 3.12, follow PEP 8, 4‑space indentation.
- Naming: snake_case for functions/vars, PascalCase for classes, UPPER_SNAKE for constants.
- Imports: prefer absolute imports consistent with PYTHONPATH=app (see above).
- Logging: use logging; format/level from app.config.Config.

## Testing Guidelines
- Framework: unittest (no pytest).
- Test files: tests/test_*.py or tests/<pkg>/test_*.py.
- Aim to cover branches and edge cases (HTML missing nodes, option merges, errors).
- Keep tests hermetic; mock network/WaterCrawlAPIClient.
- CI uploads coverage via Codecov on dev branch.

## Commit & Pull Requests
- Use Conventional Commits (seen in history):
  - feat: add movie extractor
  - fix: set PYTHONPATH properly
  - refactor: rename extractor method
- PRs should include:
  - Clear description and linked issues
  - Screenshots/logs for behavior changes (e.g., scraping output)
  - Test updates and .env.example changes when adding config

## Security & Configuration
- Do not commit secrets; use .env and keep .env.example updated.
- Required env vars:
  - WATER_CRAWL_BASE_URL, WATER_CRAWL_API_KEY, DEBUG
- Never hardcode API keys; prefer os.environ with dotenv defaults (see app/config.py).

## CI & Releases
- GitHub Actions (dev): installs deps, sets PYTHONPATH, runs unittest + coverage, uploads to Codecov.
- GitHub Actions (main/PR): semantic‑release and Docker build/push using tags.
