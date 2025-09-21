from urllib.parse import urljoin

from bs4 import BeautifulSoup
import logging

from app.models.movie import MovieListItem

logger = logging.getLogger(__name__)


class DataExtractor:
    def extract_movie_list_item(self, base_url, movie_data) -> list:
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

            movies.append(MovieListItem(
                title=title,
                cover=cover_img,
                link=full_url,
                score=score,
                meta=meta,
            ))
        return movies

    def extract_movie_details(self, movie_detail_data) -> dict:
        soup = BeautifulSoup(movie_detail_data, 'lxml')
        # 提取信息
        video_data = {
            "title": {
                "id": None,
                "current_title": None
            },
            "meta": {
                "release_date": None,
                "duration": None,
                "maker": None,
                "series": None,
                "rating": None,
                "users_reviewed": None,
                "want_to_watch": None,
                "watched": None
            },
            "tags": [],
            "actors": [],
            "cover_image": None,
            "preview_images": [],
            "magnet_links": []
        }
        # 提取视频标题和ID
        title_div = soup.find("h2", class_="title is-4")
        if title_div:
            id_tag = title_div.find("strong")
            current_title_tag = title_div.find("strong", class_="current-title")
            video_data["title"]["id"] = id_tag.text.strip() if id_tag else None
            video_data["title"]["current_title"] = (
                current_title_tag.text.strip() if current_title_tag else None
            )
        # 提取元数据
        meta_panel = soup.find("div", class_="video-meta-panel")
        if meta_panel:
            for block in meta_panel.find_all("div", class_="panel-block"):
                key_block = block.find("strong")
                if key_block:
                    key = key_block.text.strip().replace(":", "")
                    if key == "ID":
                        video_data["meta"]["id"] = block.find("span").text.strip()
                    elif key == "Released Date":
                        video_data["meta"]["release_date"] = block.find("span", class_="value").text.strip()
                    elif key == "Duration":
                        video_data["meta"]["duration"] = block.find("span", class_="value").text.strip()
                    elif key == "Maker":
                        video_data["meta"]["maker"] = block.find("span").text.strip()
                    elif key == "Series":
                        video_data["meta"]["series"] = block.find("span").text.strip()
                    elif key == "Rating":
                        rating_info = block.find("span").text.strip().split(",")
                        video_data["meta"]["rating"] = rating_info[0].strip()
                        video_data["meta"]["users_reviewed"] = rating_info[1].strip().split(" ")[-2]  # 获取用户评分数
                    elif key == "Tags":
                        for tag in block.find_all("a"):
                            video_data["tags"].append(tag.text.strip())
                    elif key == "Actor(s)":
                        for actor in block.find_all("span", class_="value"):
                            if actor.a:
                                name = actor.a.text.strip()
                            else:
                                name = "Unknown"  # 或者设置为其他默认值
                            gender = "female" if actor.find("strong", class_="symbol female") else "male"
                            video_data["actors"].append({"name": name, "gender": gender})
        # 提取封面图和预览图（封面不一定在 meta_panel 内）
        cover_image_div = soup.find("div", class_="column video-cover")
        if cover_image_div:
            cover_link = cover_image_div.find("a")
            if cover_link and cover_link.has_attr("href"):
                video_data["cover_image"] = cover_link["href"]
            # 提取预览图片
        preview_images = soup.find("div", class_="preview-images")
        if preview_images:
            for img in preview_images.find_all("a"):
                video_data["preview_images"].append(img["href"])
        # 提取磁链接信息
        magnet_links_section = soup.find("div", id="magnets")
        if magnet_links_section:
            for item in magnet_links_section.find_all("div", class_="item"):
                link_name = item.find("span", class_="name").text.strip()
                link = item.find("a")["href"]
                size_info = item.find("span", class_="meta").text.strip()
                video_data["magnet_links"].append({
                    "name": link_name,
                    "link": link,
                    "size": size_info
                })
        return video_data
