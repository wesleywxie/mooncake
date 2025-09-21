import unittest
from app.services.data_extractor import DataExtractor
from app.models.movie import MovieListItem


def _movie_item_html(href: str | None, cover: str | None, meta: str | None, title: str | None, score: str | None) -> str:
    parts = ["<div class=\"item\">", "<a class=\"box\"{}>".format(f" href=\"{href}\"" if href else "")]
    if cover:
        parts.append(f"<img src=\"{cover}\" class=\"cover\">")
    if meta is not None:
        parts.append(f"<div class=\"meta\">{meta}</div>")
    if title is not None:
        parts.append(f"<div class=\"video-title\">{title}</div>")
    if score is not None:
        parts.append(f"<div class=\"score\"><span class=\"value\">{score}</span></div>")
    parts.extend(["</a>", "</div>"])
    return "\n".join(parts)


class TestDataExtractor(unittest.TestCase):
    def setUp(self):
        """Create a fresh extractor and base URL for each test."""
        self.extractor = DataExtractor()
        self.base_url = "https://example.com"

    # ----- Movie list extraction -----
    def test_extract_movie_list_empty_input_returns_empty_list(self):
        # Act
        result = self.extractor.extract_movie_list_item(self.base_url, "")
        # Assert
        self.assertEqual(result, [])

    def test_extract_movie_list_no_items(self):
        html = '<div><p>No items here</p></div>'
        result = self.extractor.extract_movie_list_item(self.base_url, html)
        self.assertEqual(result, [])

    def test_extract_movie_list_with_valid_data(self):
        # Arrange: build two items
        html = "\n".join([
            _movie_item_html(
                href="/v/xAg1BB",
                cover="https://example.com/images/v/xAg1BB.jpg",
                meta="发布时间: 2021-11-12",
                title="Movie Title 1",
                score="9.5",
            ),
            _movie_item_html(
                href="/v/yBc2CC",
                cover="https://example.com/images/v/yBc2CC.jpg",
                meta="发布时间: 2022-03-15",
                title="Another Movie Title",
                score="8.7",
            ),
        ])
        expected = [
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
        # Act
        result = self.extractor.extract_movie_list_item(self.base_url, html)
        # Assert
        self.assertEqual(result, expected)

    def test_extract_movie_list_handles_missing_fields(self):
        # Arrange
        html = _movie_item_html(
            href="/v/zZzZZz",
            cover="https://example.com/images/movie1.jpg",
            meta=None,
            title=None,
            score=None,
        )
        expected = [MovieListItem(
            title=None,
            score=None,
            meta=None,
            cover='https://example.com/images/movie1.jpg',
            link='https://example.com/v/zZzZZz',
        )]
        # Act
        result = self.extractor.extract_movie_list_item(self.base_url, html)
        # Assert
        self.assertEqual(result, expected)

    def test_extract_movie_list_without_cover_or_link(self):
        html = '<div class="item"><div class="video-title">Movie Without Image or Link</div></div>'
        expected = [MovieListItem(title='Movie Without Image or Link', score=None, meta=None, cover=None, link=None)]
        result = self.extractor.extract_movie_list_item(self.base_url, html)
        self.assertEqual(result, expected)

    # ----- Movie details extraction -----
    def test_extract_full_movie_details(self):
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
        html = '<div class="video-meta-panel"></div>'
        result = self.extractor.extract_movie_details(html)
        self.assertIsNone(result["title"]["id"])
        self.assertIsNone(result["title"]["current_title"])

    def test_missing_meta_panel(self):
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
        html = '<h2 class="title is-4"><strong>ID123</strong></h2><div class="video-meta-panel"></div>'
        result = self.extractor.extract_movie_details(html)
        self.assertIsNone(result["cover_image"])

    def test_missing_preview_images(self):
        html = '<h2 class="title is-4"><strong>ID123</strong></h2><div class="video-meta-panel"></div>'
        result = self.extractor.extract_movie_details(html)
        self.assertEqual(result["preview_images"], [])

    def test_missing_magnet_links(self):
        html = '<h2 class="title is-4"><strong>ID123</strong></h2><div class="video-meta-panel"></div>'
        result = self.extractor.extract_movie_details(html)
        self.assertEqual(result["magnet_links"], [])

    def test_multiple_magnet_links(self):
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

