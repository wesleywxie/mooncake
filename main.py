import logging

from app.config import Config

config = Config()
logging.basicConfig(format=config.LOGGING_FORMAT, level=config.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def main():
    logger.info(f"WATER_CRAWL_API_KEY: {config.WATER_CRAWL_API_KEY}")
    logger.info(f"调试模式: {config.DEBUG}")


if __name__ == "__main__":
    main()
