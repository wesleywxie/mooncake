import json
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class DataExtractor:
    def extract_movie_list_item(self, base_url, movie_data):
        soup = BeautifulSoup(movie_data, 'lxml')
        movies = []
        for item in soup.select('.item'):
            title_elem = item.select_one('.video-title')
            score_elem = item.select_one('.score .value')
            meta_elem = item.select_one('.meta')
            cover_img_elem = item.select_one('.cover')
            link_elem = item.select_one('a')

            title = title_elem.get_text(strip=True) if title_elem else None
            score = score_elem.get_text(strip=True) if score_elem else None
            meta = meta_elem.get_text(strip=True) if meta_elem else None
            cover_img = cover_img_elem['src'] if cover_img_elem and 'src' in cover_img_elem.attrs else None
            link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
            full_url = urljoin(base_url, link) if link else None

            movies.append({
                'title': title,
                'score': score,
                'meta': meta,
                'cover_img': cover_img,
                'link': full_url,
            })
        return movies
