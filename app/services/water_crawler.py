try:
    from watercrawl import WaterCrawlAPIClient  # type: ignore

    _HAVE_WATERCRAWL = True
except Exception:  # pragma: no cover - exercised by environments without dependency
    WaterCrawlAPIClient = None  # type: ignore
    _HAVE_WATERCRAWL = False

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
    "actions": [],
    # actions to perform {"type": "screenshot"} or {"type": "pdf"}
}


class WaterCrawler:
    def __init__(self, base_url: str, api_key: str):
        # Lazy init to support environments without the dependency and easier testing
        self._base_url = base_url
        self._api_key = api_key
        self.client = None

    def scrape(self, url: str, page_options: dict) -> dict:
        merged_options = {**default_options, **page_options}
        if self.client is None:
            if not _HAVE_WATERCRAWL:
                raise ImportError(
                    name="WaterCrawler is required",
                    msg="WaterCrawler requires the WaterCrawl API client.",
                )
            # Instantiate the client lazily
            self.client = WaterCrawlAPIClient(
                base_url=self._base_url, api_key=self._api_key
            )
        return self.client.scrape_url(
            url=url,
            page_options=merged_options,
        )
