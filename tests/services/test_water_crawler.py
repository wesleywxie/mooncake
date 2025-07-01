import unittest
from unittest.mock import patch, MagicMock

from app.services.water_crawler import WaterCrawler


class TestWaterCrawlerScrape(unittest.TestCase):
    def setUp(self):
        """初始化测试环境"""
        self.crawler = WaterCrawler('base_url', 'some-api-key')
        # 假设 WaterCrawler 类有一个 client 实例属性
        self.crawler.client = MagicMock()

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html'})
    def test_scrape_with_valid_options(self):
        """TC01: 验证正常调用时合并选项并调用客户端"""
        # Arrange
        url = "https://example.com"
        page_options = {'timeout': 30, 'screenshot': True}
        expected_options = {'timeout': 30, 'format': 'html', 'screenshot': True}

        # Act
        result = self.crawler.scrape(url, page_options)

        # Assert
        self.crawler.client.scrape_url.assert_called_once_with(
            url=url,
            page_options=expected_options
        )
        # 假设 scrape_url 返回值直接返回给调用者
        self.assertEqual(result, self.crawler.client.scrape_url.return_value)

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html'})
    def test_scrape_with_empty_options(self):
        """TC02: 验证空 page_options 使用默认值"""
        # Arrange
        url = "https://example.com"
        page_options = {}
        expected_options = {'timeout': 10, 'format': 'html'}

        # Act
        result = self.crawler.scrape(url, page_options)

        # Assert
        self.crawler.client.scrape_url.assert_called_once_with(
            url=url,
            page_options=expected_options
        )
        self.assertEqual(result, self.crawler.client.scrape_url.return_value)

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html', 'proxy': None})
    def test_scrape_overrides_default_options(self):
        """TC03: 验证自定义选项覆盖默认值"""
        # Arrange
        url = "https://example.com"
        page_options = {'timeout': 5, 'proxy': 'http://myproxy.com'}
        expected_options = {'timeout': 5, 'format': 'html', 'proxy': 'http://myproxy.com'}

        # Act
        result = self.crawler.scrape(url, page_options)

        # Assert
        self.crawler.client.scrape_url.assert_called_once_with(
            url=url,
            page_options=expected_options
        )
        self.assertEqual(result, self.crawler.client.scrape_url.return_value)

    @patch('app.services.water_crawler.default_options', {'timeout': 10, 'format': 'html'})
    def test_scrape_client_throws_exception(self):
        """TC04: 验证当客户端抛出异常时处理正确"""
        # Arrange
        url = "https://example.com"
        page_options = {'timeout': 30}
        self.crawler.client.scrape_url.side_effect = Exception("Network error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.crawler.scrape(url, page_options)

        self.assertTrue("Network error" in str(context.exception))
        self.crawler.client.scrape_url.assert_called_once_with(
            url=url,
            page_options={'timeout': 30, 'format': 'html'}
        )


if __name__ == '__main__':
    unittest.main()
