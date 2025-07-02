import unittest
from app.services.data_extractor import DataExtractor


class TestDataExtractor(unittest.TestCase):
    def setUp(self):
        """初始化测试环境"""
        self.extractor = DataExtractor()
        self.base_url = "https://example.com"

    def test_extract_movies_empty_input(self):
        """
        TC04: 测试空输入
        验证返回空列表
        """
        result = self.extractor.extract_movie_list_item(self.base_url, "")
        self.assertEqual(result, [])

    def test_extract_movies_no_items(self):
        """
        TC05: 测试 HTML 中无 .item 元素
        验证返回空列表
        """
        html = '<div><p>No items here</p></div>'
        result = self.extractor.extract_movie_list_item(self.base_url, html)
        self.assertEqual(result, [])

    def test_extract_movies_with_valid_data(self):
        """
        TC01: 测试正常 HTML 数据提取
        验证所有字段都能正确提取并拼接 URL
        """
        html = '''
        <div class="item">
            <a href="/v/xAg1BB" class="box" title="Movie Title 1 - Actress Name">
                <img src="https://example.com/images/v/xAg1BB.jpg" class="cover">
                <div class="meta">发布时间: 2021-11-12</div>
                <div class="video-title">Movie Title 1</div>
                <div class="score"><span class="value">9.5</span></div>
            </a>
        </div>
        <div class="item">
            <a href="/v/yBc2CC" class="box" title="Another Movie - Actress Name">
                <img src="https://example.com/images/v/yBc2CC.jpg" class="cover">
                <div class="meta">发布时间: 2022-03-15</div>
                <div class="video-title">Another Movie Title</div>
                <div class="score"><span class="value">8.7</span></div>
            </a>
        </div>
        '''
        expected_result = [
            {
                'title': 'Movie Title 1',
                'score': '9.5',
                'meta': '发布时间: 2021-11-12',
                'cover_img': 'https://example.com/images/v/xAg1BB.jpg',
                'link': 'https://example.com/v/xAg1BB',
            },
            {
                'title': 'Another Movie Title',
                'score': '8.7',
                'meta': '发布时间: 2022-03-15',
                'cover_img': 'https://example.com/images/v/yBc2CC.jpg',
                'link': 'https://example.com/v/yBc2CC',
            }
        ]
        result = self.extractor.extract_movie_list_item("https://example.com", html)
        self.assertEqual(result, expected_result)

    def test_extract_movies_missing_score_or_meta(self):
        """
        TC02: 测试部分字段缺失的情况
        验证即使某些字段缺失也能继续解析
        """
        html = '''
        <div class="item">
            <a href="/v/zZzZZz" class="box" title="Untitled Movie">
                <img src="https://example.com/images/movie1.jpg" class="cover">
            </a>
        </div>
        '''
        expected_result = [
            {
                'title': None,
                'score': None,
                'meta': None,
                'cover_img': 'https://example.com/images/movie1.jpg',
                'link': 'https://example.com/v/zZzZZz',
            }
        ]
        result = self.extractor.extract_movie_list_item("https://example.com", html)
        self.assertEqual(result, expected_result)

    def test_extract_movies_missing_cover_or_link(self):
        """
        TC03: 测试缺少 cover img 或 a 标签的情况
        验证不会抛出异常，对应字段为 None
        """
        html = '''
        <div class="item">
            <div class="video-title">Movie Without Image or Link</div>
        </div>
        '''
        expected_result = [
            {
                'title': 'Movie Without Image or Link',
                'score': None,
                'meta': None,
                'cover_img': None,
                'link': None,
            }
        ]
        result = self.extractor.extract_movie_list_item("https://example.com", html)
        self.assertEqual(result, expected_result)
