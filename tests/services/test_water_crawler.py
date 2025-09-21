import unittest
from unittest.mock import patch, MagicMock

from app.services.water_crawler import WaterCrawler


class TestWaterCrawlerScrape(unittest.TestCase):
    def setUp(self):
        """Set up a crawler with a mocked client."""
        self.crawler = WaterCrawler('base_url', 'some-api-key')
        self.crawler.client = MagicMock()

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html'})
    def test_scrape_merges_options_and_calls_client(self):
        """Merges page options over defaults and forwards to client."""
        # Arrange
        url = "https://example.com"
        page_options = {'timeout': 30, 'screenshot': True}
        expected_options = {'timeout': 30, 'format': 'html', 'screenshot': True}

        # Act
        result = self.crawler.scrape(url, page_options)

        # Assert
        self.crawler.client.scrape_url.assert_called_once_with(url=url, page_options=expected_options)
        self.assertEqual(result, self.crawler.client.scrape_url.return_value)

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html'})
    def test_scrape_uses_defaults_when_empty(self):
        """Uses default options when page_options is empty."""
        # Arrange
        url = "https://example.com"
        page_options = {}
        expected_options = {'timeout': 10, 'format': 'html'}

        # Act
        result = self.crawler.scrape(url, page_options)

        # Assert
        self.crawler.client.scrape_url.assert_called_once_with(url=url, page_options=expected_options)
        self.assertEqual(result, self.crawler.client.scrape_url.return_value)

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html', 'proxy': None})
    def test_scrape_overrides_default_options(self):
        """Custom options override defaults and are forwarded."""
        # Arrange
        url = "https://example.com"
        page_options = {'timeout': 5, 'proxy': 'http://myproxy.com'}
        expected_options = {'timeout': 5, 'format': 'html', 'proxy': 'http://myproxy.com'}

        # Act
        result = self.crawler.scrape(url, page_options)

        # Assert
        self.crawler.client.scrape_url.assert_called_once_with(url=url, page_options=expected_options)
        self.assertEqual(result, self.crawler.client.scrape_url.return_value)

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html'})
    def test_scrape_bubbles_up_client_exceptions(self):
        """Propagates client exceptions and leaves call intact."""
        # Arrange
        url = "https://example.com"
        page_options = {'timeout': 30}
        self.crawler.client.scrape_url.side_effect = Exception("Network error")

        # Act & Assert
        with self.assertRaises(Exception) as ctx:
            self.crawler.scrape(url, page_options)

        self.assertIn("Network error", str(ctx.exception))
        self.crawler.client.scrape_url.assert_called_once_with(url=url, page_options={'timeout': 30, 'format': 'html'})


if __name__ == '__main__':
    unittest.main()
