import logging

from app.ext import CONFIG, CRAWLER
from app.db import init_db, get_session
from app.services.data_extractor import DataExtractor
from app.services.repository import MovieDetailsRepository


logging.basicConfig(format=CONFIG.LOGGING_FORMAT, level=CONFIG.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def run():
    # Ensure tables exist
    init_db()

    url = "https://javdb.com/censored?page=1"
    logger.info("Scraping list page: %s", url)
    result = CRAWLER.scrape(
        url=url,
        page_options={
            "include_tags": [".movie-list"],
            "include_html": True,
            "only_main_content": True,
            "include_links": False,
        },
    )

    html_content = result.get("result", {}).get("html", "")
    extractor = DataExtractor()
    movie_list = extractor.extract_movie_list_item(base_url=url, movie_data=html_content)
    logger.info("Found %d movies. Fetching details and saving...", len(movie_list))

    with get_session() as session:
        repo = MovieDetailsRepository(session)
        for item in movie_list:
            if not item.link:
                continue
            try:
                detail_html = CRAWLER.scrape(
                    url=item.link,
                    page_options={
                        "include_tags": [".video-detail"],
                        "include_html": True,
                        "only_main_content": True,
                        "include_links": False,
                    },
                ).get("result", {}).get("html", "")
                details = extractor.extract_movie_details(detail_html)
                repo.upsert_from_details(details)
            except Exception as e:
                logger.warning("Failed to process %s: %s", item.link, e)

    logger.info("Done.")


if __name__ == "__main__":
    run()
