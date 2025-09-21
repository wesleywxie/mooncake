# mooncake

[![CI (dev)](https://github.com/wesleywxie/mooncake/actions/workflows/dev.yml/badge.svg?branch=dev)](https://github.com/wesleywxie/mooncake/actions/workflows/dev.yml)
[![CI (build)](https://github.com/wesleywxie/mooncake/actions/workflows/build.yml/badge.svg)](https://github.com/wesleywxie/mooncake/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/wesleywxie/mooncake/branch/dev/graph/badge.svg)](https://codecov.io/gh/wesleywxie/mooncake)
![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Mooncake is a small, testable scraping toolkit that uses the WaterCrawl API to fetch HTML, extracts structured movie details with BeautifulSoup, and persists them with SQLAlchemy.

It’s designed to be simple to run locally, easy to test, and safe to extend.

<!-- toc -->
- [Features](#features)
- [Project Structure](#project-structure)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [Usage](#usage)
- [Data Model](#data-model)
- [Development](#development)
- [Testing](#testing)
- [CI](#ci)
- [Contributing](#contributing)
- [Security](#security)
- [Roadmap](#roadmap)
- [License](#license)
<!-- tocstop -->

## Features

- Fetches pages via WaterCrawl’s hosted API client (no local browser required)
- Extracts movie list items and rich movie details from HTML with BeautifulSoup
- Persists normalized movie details to a relational DB via SQLAlchemy
- Clean configuration via `.env` and environment variables
- Fully unit tested with `unittest`; coverage uploaded on `dev` branch

## Project Structure

```
app/
  config.py            # App configuration (.env + env vars)
  ext.py               # App-wide singletons (CONFIG, CRAWLER)
  db.py                # SQLAlchemy engine/session helpers
  models/
    movie.py           # MovieListItem (parsed list item DTO)
    movie_orm.py       # ORM models for movie details
  services/
    data_extractor.py  # BeautifulSoup parsing helpers
    water_crawler.py   # WaterCrawl API wrapper
    repository.py      # Repositories to persist movie data
examples/
  save_movies.py       # Example: scrape and persist details
tests/                 # Unit tests (unittest)
main.py                # Simple smoke-runner for scraping
requirements.txt       # Python dependencies
.env.example           # Sample env config
```

## Quickstart

Prerequisites:

- Python 3.12+
- A WaterCrawl API key (see: https://app.watercrawl.dev)

Set up and run locally:

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)/app

# Configure env vars (see .env.example). Example:
cp .env.example .env
edit .env  # add your WATER_CRAWL_API_KEY

# Smoke run (prints parsed details to stdout)
python main.py
```

Persist scraped details to the database (uses `DATABASE_URL` or falls back to `sqlite:///mooncake.db`):

```
python examples/save_movies.py
```

## Configuration

Mooncake reads from `.env` (if present) and then environment variables (env vars override `.env`). Required and optional keys:

- `WATER_CRAWL_BASE_URL` (required) — default: `https://app.watercrawl.dev`
- `WATER_CRAWL_API_KEY` (required) — your API key
- `DATABASE_URL` (optional) — SQLAlchemy URL e.g. `sqlite:///mooncake.db`, `postgresql+psycopg://user:pass@host/db`
- `DEBUG` (optional) — `True` or `False` (enables verbose logging)

See `.env.example:1` for a reference.

## Usage

Two common entry points:

- `main.py:1` — Scrapes a list page and prints extracted details to the log (no persistence). Useful as a smoke test.
- `examples/save_movies.py:1` — Scrapes a list page, follows item links, parses full details, and upserts them into the DB.

Under the hood:

- `app/ext.py:1` wires `Config` and `WaterCrawler` singletons.
- `app/services/data_extractor.py:1` parses list and detail HTML into Python data structures.
- `app/db.py:1` provides `init_db()` and `get_session()` helpers.
- `app/services/repository.py:1` contains `MovieDetailsRepository.upsert_from_details(...)` to persist the details dict.

## Data Model

ORM entities used for persistence (`app/models/movie_orm.py:1`):

- `Movie` — core record (code, title, maker, release_date, cover_image, rating_text, users_reviewed, etc.)
- `PreviewImage` — one-to-many preview images
- `MovieTag` — one-to-many tags
- `Actor` — de-duplicated actor table
- `MovieActor` — many-to-many junction between movies and actors
- `MagnetLink` — one-to-many magnet links

Tables are created automatically by `init_db()`; for production, prefer migrations (e.g. Alembic).

## Development

- Create a virtualenv and install dependencies:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
- Set module path for absolute imports:
  - `export PYTHONPATH=$(pwd)/app`
- Coding standards:
  - Python 3.12, PEP 8, 4-space indentation
  - Type hints use PEP 604 unions (`T | None`) and built-in generics (`list`, `dict`, ...)
  - Logging respects format/level from `app.config.Config`
  - Follow Conventional Commits in PRs (e.g., `feat:`, `fix:`, `refactor:`)

## Testing

Run the test suite:

```
python -m unittest discover tests
```

Generate coverage locally:

```
pip install coverage
coverage run -m unittest discover tests && coverage report
```

Testing guidelines:

- Keep tests hermetic; mock network calls (`WaterCrawlAPIClient`)
- Prefer AAA (Arrange-Act-Assert) structure and descriptive names
- Target edge cases (missing HTML nodes, option merges, errors)

## CI

GitHub Actions workflows:

- `.github/workflows/dev.yml:1` (branch `dev`): installs deps, sets `PYTHONPATH`, runs `unittest` + coverage, uploads to Codecov.
- `.github/workflows/build.yml:1` (PRs to `main`): semantic release and Docker build/push using tags (requires repo secrets and variables).

## Contributing

- Use Conventional Commits for messages.
- PRs should include:
  - Clear description and linked issues
  - Logs/screenshots for behavior changes (e.g., scraping output)
  - Updated tests and `.env.example` when adding config

## Security

- Never commit secrets. Use `.env` locally; keep `.env.example` updated for new keys.
- Required env vars: `WATER_CRAWL_BASE_URL`, `WATER_CRAWL_API_KEY`, `DEBUG` (optional), `DATABASE_URL` (optional).

## Roadmap

- Alembic migrations for schema changes
- CLI commands for scraping and persistence
- Option to export results as JSON/CSV
- Dockerfile and published image (paired with the release workflow)

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` for details.
