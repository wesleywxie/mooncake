from app.config import Config
from services.water_crawler import WaterCrawler

CONFIG = Config()

CRAWLER = WaterCrawler(base_url=CONFIG.WATER_CRAWL_BASE_URL, api_key=CONFIG.WATER_CRAWL_API_KEY)
