import logging

from app.ext import CONFIG, CRAWLER
from app.services.data_extractor import DataExtractor

logging.basicConfig(format=CONFIG.LOGGING_FORMAT, level=CONFIG.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def main():
    url = "https://javdb.com/censored?page=1"
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
    movie_list = extractor.extract_movie_list_item(base_url=url, movie_data=html_content)

    for movie_list_item in movie_list:
        html_content = CRAWLER.scrape(
            url=movie_list_item.link,
            page_options={
                "include_tags": [".video-detail"],
                "include_html": True,
                "only_main_content": True,
                "include_links": False,
            },
        ).get("result").get("html")
        movie_details = extractor.extract_movie_details(html_content)
        logger.debug(movie_details)



if __name__ == "__main__":
    main()
