import logging

from app.ext import CONFIG

logging.basicConfig(format=CONFIG.LOGGING_FORMAT, level=CONFIG.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def main():
    logger.info(f"WATER_CRAWL_API_KEY: {CONFIG.WATER_CRAWL_API_KEY}")
    logger.info(f"调试模式: {CONFIG.DEBUG}")


if __name__ == "__main__":
    main()
