# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the mooncake project.

## Project Overview

Mooncake is a small, testable scraping toolkit that uses the WaterCrawl API to fetch HTML, extracts structured movie details with BeautifulSoup, and persists them with SQLAlchemy. It’s designed to be simple to run locally, easy to test, and safe to extend.

**Key Technologies:**

*   **Python 3.12+**
*   **WaterCrawl API:** For fetching web pages.
*   **BeautifulSoup:** For parsing HTML and extracting data.
*   **SQLAlchemy:** For persisting data to a database.

**Architecture:**

The project is structured into the following directories:

*   `app/`: Contains the core application logic.
    *   `config.py`: Handles application configuration from `.env` files and environment variables.
    *   `ext.py`: Manages app-wide singletons like the configuration and the WaterCrawl API client.
    *   `db.py`: Provides SQLAlchemy engine and session helpers.
    *   `models/`: Defines the data transfer objects (`movie.py`) and ORM models (`movie_orm.py`).
    *   `services/`: Includes the data extraction logic (`data_extractor.py`), the WaterCrawl API wrapper (`water_crawler.py`), and the database repository (`repository.py`).
*   `examples/`: Contains example scripts for using the toolkit.
*   `tests/`: Includes unit tests for the application.

## Building and Running

**1. Set up the environment:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)/app
```

**2. Configure environment variables:**

Copy the `.env.example` file to `.env` and add your WaterCrawl API key.

```bash
cp .env.example .env
# Edit .env to add your WATER_CRAWL_API_KEY
```

**3. Run the application:**

*   **Smoke Test:** To scrape a page and print the extracted details to the console:

    ```bash
    python main.py
    ```

*   **Save to Database:** To scrape and persist the details to a database:

    ```bash
    python examples/save_movies.py
    ```

**4. Run tests:**

```bash
python -m unittest discover tests
```

## Development Conventions

*   **Coding Style:**
    *   Python 3.12+
    *   PEP 8 with 4-space indentation.
    *   Type hints using PEP 604 unions (`T | None`) and built-in generics (`list`, `dict`).
*   **Commits:** Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
*   **Pull Requests:**
    *   Provide a clear description and link to any relevant issues.
    *   Include logs or screenshots for any behavioral changes.
    *   Update tests and `.env.example` when adding new configurations.
