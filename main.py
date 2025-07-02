import logging

from app.ext import CONFIG, CRAWLER
from services.data_extractor import DataExtractor

logging.basicConfig(format=CONFIG.LOGGING_FORMAT, level=CONFIG.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def main():
    url = "https://javdb.com/censored?page=1",
    result = CRAWLER.scrape(
        url=url,
        page_options={
            "include_tags": [".movie-list"],
            "include_html": True,
            "only_main_content": True,
            "include_links": False,
        },
    )

    html_content = result.get("result").get("html")
    extractor = DataExtractor()
    movies_json = extractor.extract_movie_list_item(base_url=url, movie_data=html_content)
    logger.info(movies_json)


if __name__ == "__main__":
    main()
