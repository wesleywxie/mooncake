import os
from dotenv import dotenv_values


class Config:

    def __init__(self):
        values = {
            **dotenv_values(".env"),  # load dot env variables
            **os.environ,  # override loaded values with environment variables
        }

        self.WATER_CRAWL_API_KEY = values.get("WATER_CRAWL_API_KEY")
        self.DEBUG = values.get("DEBUG", "False").lower() == "true"
