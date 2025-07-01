import logging
import os
from dotenv import dotenv_values


class Config:

    def __init__(self):
        values = {
            **dotenv_values(".env"),  # load dot env variables
            **os.environ,  # override loaded values with environment variables
        }

        self.DEBUG = values.get("DEBUG", "False").lower() == "true"
        self.WATER_CRAWL_BASE_URL = values.get("WATER_CRAWL_BASE_URL")
        self.WATER_CRAWL_API_KEY = values.get("WATER_CRAWL_API_KEY")
        self.LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s %(name)s] - %(message)s"
        self.LOGGING_LEVEL = logging.DEBUG if self.DEBUG else logging.INFO

