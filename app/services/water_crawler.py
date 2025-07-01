from watercrawl import WaterCrawlAPIClient

default_options = {
    "exclude_tags": [],  # exclude tags from the page
    "include_tags": [],  # include tags from the page
    "wait_time": 1000,  # wait time in milliseconds after page load
    "include_html": True,  # the result will include HTML
    "only_main_content": True,
    # only main content of the page automatically remove headers, footers, etc.
    "include_links": False,  # if True the result will include links
    "timeout": 15000,  # timeout in milliseconds
    "accept_cookies_selector": None,
    # accept cookies selector e.g. "#accept-cookies"
    "locale": "en-US",  # locale
    "extra_headers": {},
    # extra headers e.g. {"Authorization": "Bearer your_token"}
    "actions": []
    # actions to perform {"type": "screenshot"} or {"type": "pdf"}
}


class WaterCrawler:
    def __init__(self, base_url: str, api_key: str):
        self.client = WaterCrawlAPIClient(base_url=base_url, api_key=api_key)

    def scrape(self, url: str, page_options: dict) -> dict:
        merged_options = {**default_options, **page_options}
        return self.client.scrape_url(
            url=url,
            page_options=merged_options,
        )
