import logging

from app.ext import CONFIG

logging.basicConfig(format=CONFIG.LOGGING_FORMAT, level=CONFIG.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting...")


if __name__ == "__main__":
    main()
