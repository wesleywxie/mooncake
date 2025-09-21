import unittest
from app.services.data_extractor import DataExtractor
from app.models.movie import MovieListItem


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
            MovieListItem(
                title='Movie Title 1',
                score='9.5',
                meta='发布时间: 2021-11-12',
                cover='https://example.com/images/v/xAg1BB.jpg',
                link='https://example.com/v/xAg1BB'
            ),
            MovieListItem(
                title='Another Movie Title',
                score='8.7',
                meta='发布时间: 2022-03-15',
                cover='https://example.com/images/v/yBc2CC.jpg',
                link='https://example.com/v/yBc2CC'
            ),
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
        expected_result = [MovieListItem(
            title=None,
            score=None,
            meta=None,
            cover='https://example.com/images/movie1.jpg',
            link='https://example.com/v/zZzZZz',
        )]
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
            MovieListItem(
                title='Movie Without Image or Link',
                score=None,
                meta=None,
                cover=None,
                link=None,
            )
        ]
        result = self.extractor.extract_movie_list_item("https://example.com", html)
        self.assertEqual(result, expected_result)

    def test_extract_full_movie_details(self):
        """TC01: 完整数据提取"""
        html = '''
        <h2 class="title is-4">
            <strong>ID123</strong>
            <strong class="current-title">Movie Title</strong>
        </h2>
        <div class="video-meta-panel">
            <div class="panel-block"><strong>Released Date:</strong><span class="value">2023-01-01</span></div>
            <div class="panel-block"><strong>Duration:</strong><span class="value">120 min</span></div>
            <div class="panel-block"><strong>Maker:</strong><span>Studio A</span></div>
            <div class="panel-block"><strong>Series:</strong><span>Series B</span></div>
            <div class="panel-block"><strong>Rating:</strong><span>⭐️⭐️⭐️⭐️⭐️, 100 reviews</span></div>
            <div class="panel-block"><strong>Tags:</strong><a href="#">Tag1</a><a href="#">Tag2</a></div>
            <div class="panel-block"><strong>Actor(s):</strong><span class="value"><a href="#">Actor1</a></span></div>
        </div>
        <div class="column video-cover"><a href="/cover.jpg">Cover</a></div>
        <div class="preview-images">
            <a href="/img1.jpg"></a>
            <a href="/img2.jpg"></a>
        </div>
        <div id="magnets">
            <div class="item">
                <span class="name">Link1</span>
                <a href="magnet:?xt=urn:btih:abc123">Download</a>
                <span class="meta">1.2 GB</span>
            </div>
        </div>
        '''
        result = self.extractor.extract_movie_details(html)
        self.assertEqual(result["title"]["id"], "ID123")
        self.assertEqual(result["title"]["current_title"], "Movie Title")
        self.assertEqual(result["meta"]["release_date"], "2023-01-01")
        self.assertEqual(result["meta"]["duration"], "120 min")
        self.assertEqual(result["meta"]["maker"], "Studio A")
        self.assertEqual(result["meta"]["series"], "Series B")
        self.assertEqual(result["meta"]["rating"], "⭐️⭐️⭐️⭐️⭐️")
        self.assertEqual(result["meta"]["users_reviewed"], "100")
        self.assertIn("Tag1", result["tags"])
        self.assertEqual(len(result["actors"]), 1)
        self.assertEqual(result["cover_image"], "/cover.jpg")
        self.assertEqual(len(result["preview_images"]), 2)
        self.assertEqual(len(result["magnet_links"]), 1)

    def test_missing_title(self):
        """TC02: 缺失标题部分"""
        html = '<div class="video-meta-panel"></div>'
        result = self.extractor.extract_movie_details(html)
        self.assertIsNone(result["title"]["id"])
        self.assertIsNone(result["title"]["current_title"])

    def test_missing_meta_panel(self):
        """TC03: 缺失元数据面板"""
        html = '<h2 class="title is-4"><strong>ID123</strong></h2>'
        result = self.extractor.extract_movie_details(html)
        self.assertIsNone(result["meta"]["release_date"])
        self.assertIsNone(result["meta"]["duration"])
        self.assertIsNone(result["meta"]["maker"])
        self.assertIsNone(result["meta"]["series"])
        self.assertIsNone(result["meta"]["rating"])
        self.assertIsNone(result["meta"]["users_reviewed"])
        self.assertEqual(result["tags"], [])
        self.assertEqual(result["actors"], [])

    def test_missing_cover_image(self):
        """TC05: 缺失封面图"""
        html = '''
        <h2 class="title is-4"><strong>ID123</strong></h2>
        <div class="video-meta-panel"></div>
        '''
        result = self.extractor.extract_movie_details(html)
        self.assertIsNone(result["cover_image"])

    def test_missing_preview_images(self):
        """TC06: 缺失预览图"""
        html = '''
        <h2 class="title is-4"><strong>ID123</strong></h2>
        <div class="video-meta-panel"></div>
        '''
        result = self.extractor.extract_movie_details(html)
        self.assertEqual(result["preview_images"], [])

    def test_missing_magnet_links(self):
        """TC07: 缺失磁力链接"""
        html = '''
        <h2 class="title is-4"><strong>ID123</strong></h2>
        <div class="video-meta-panel"></div>
        '''
        result = self.extractor.extract_movie_details(html)
        self.assertEqual(result["magnet_links"], [])

    def test_multiple_magnet_links(self):
        """TC08: 多个磁力链接"""
        html = '''
        <div id="magnets">
            <div class="item">
                <span class="name">Link1</span>
                <a href="magnet:?xt=urn:btih:abc123">Download</a>
                <span class="meta">1.2 GB</span>
            </div>
            <div class="item">
                <span class="name">Link2</span>
                <a href="magnet:?xt=urn:btih:def456">Download</a>
                <span class="meta">2.5 GB</span>
            </div>
        </div>
        '''
        result = self.extractor.extract_movie_details(html)
        self.assertEqual(len(result["magnet_links"]), 2)
        self.assertEqual(result["magnet_links"][0]["link"], "magnet:?xt=urn:btih:abc123")
        self.assertEqual(result["magnet_links"][1]["link"], "magnet:?xt=urn:btih:def456")

    def test_special_rating_format(self):
        """TC09: 特殊评分格式"""
        html = '''
        <div class="video-meta-panel">
            <div class="panel-block">
                <strong>Rating:</strong>
                <span>⭐️⭐️⭐️⭐️, 50 reviews</span>
            </div>
        </div>
        '''
        result = self.extractor.extract_movie_details(html)
        self.assertEqual(result["meta"]["rating"], "⭐️⭐️⭐️⭐️")
        self.assertEqual(result["meta"]["users_reviewed"], "50")

    def test_empty_input(self):
        """TC10: 空输入"""
        html = ''
        result = self.extractor.extract_movie_details(html)
        self.assertIsNone(result["title"]["id"])
        self.assertIsNone(result["title"]["current_title"])
        self.assertIsNone(result["meta"]["release_date"])
        self.assertIsNone(result["meta"]["duration"])
        self.assertIsNone(result["meta"]["maker"])
        self.assertIsNone(result["meta"]["series"])
        self.assertIsNone(result["meta"]["rating"])
        self.assertIsNone(result["meta"]["users_reviewed"])
        self.assertEqual(result["tags"], [])
        self.assertEqual(result["actors"], [])
        self.assertIsNone(result["cover_image"])
        self.assertEqual(result["preview_images"], [])
        self.assertEqual(result["magnet_links"], [])


if __name__ == '__main__':
    unittest.main()
