from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.models.movie import MovieListItem

logger = logging.getLogger(__name__)


class DataExtractor:
    """HTML data extraction helpers for movie list and details pages.

    Methods keep a stable public API but the internals are organized
    into small helpers for clarity and easier maintenance.
    """

    def extract_movie_list_item(self, base_url: str, movie_data: str) -> list[MovieListItem]:
        """Extract a list of MovieListItem from a movie listing HTML snippet.

        - Safely handles missing nodes by returning None for absent fields.
        - Joins relative links against the provided base URL.
        """
        soup = BeautifulSoup(movie_data, "lxml")
        movies: list[MovieListItem] = []

        for item in soup.select(".item"):
            movie_id = self._get_text(item.select_one(".video-title strong"))
            title = self._get_text(item.select_one(".video-title"))
            score = self._get_text(item.select_one(".score .value"))
            meta = self._get_text(item.select_one(".meta"))
            cover_img = self._get_attr(item.select_one(".cover"), "src")

            link = self._get_attr(item.select_one("a"), "href")
            full_url = urljoin(base_url, link) if link else None

            movies.append(
                MovieListItem(
                    id=movie_id,
                    title=title,
                    cover=cover_img,
                    link=full_url,
                    score=score,
                    meta=meta,
                )
            )

        return movies

    def extract_movie_details(self, movie_detail_data: str) -> dict[str, Any]:
        """Extract a structured dictionary of movie details from HTML."""
        soup = BeautifulSoup(movie_detail_data, "lxml")

        video_data: dict[str, Any] = {
            "title": {"id": None, "current_title": None},
            "meta": {
                "release_date": None,
                "duration": None,
                "maker": None,
                "series": None,
                "rating": None,
                "users_reviewed": None,
                "want_to_watch": None,
                "watched": None,
            },
            "tags": [],
            "actors": [],
            "cover_image": None,
            "preview_images": [],
            "magnet_links": [],
        }

        self._parse_title(soup, video_data)
        self._parse_meta_panel(soup, video_data)
        self._parse_cover_and_previews(soup, video_data)
        self._parse_magnet_links(soup, video_data)

        return video_data

    # -------------------------
    # Internal helper functions
    # -------------------------

    @staticmethod
    def _get_text(node: Tag | None) -> str | None:
        """Return stripped text of node or None if node is falsy."""
        return node.get_text(strip=True) if node else None

    @staticmethod
    def _get_attr(node: Tag | None, attr: str) -> str | None:
        """Return attribute value or None if node/attribute absent."""
        if node and attr in node.attrs:
            value = node.attrs.get(attr)
            if isinstance(value, list):
                return value[0] if value else None
            return str(value)
        return None

    def _parse_title(self, soup: BeautifulSoup, out: dict[str, Any]) -> None:
        title_div = soup.find("h2", class_="title is-4")
        if not title_div:
            return

        id_tag = title_div.find("strong")
        current_title_tag = title_div.find("strong", class_="current-title")
        out["title"]["id"] = self._get_text(id_tag)
        out["title"]["current_title"] = self._get_text(current_title_tag)

    def _parse_meta_panel(self, soup: BeautifulSoup, out: dict[str, Any]) -> None:
        meta_panel = soup.find("div", class_="video-meta-panel")
        if not meta_panel:
            return

        for block in meta_panel.find_all("div", class_="panel-block"):
            key_block = block.find("strong")
            if not key_block:
                continue

            key = key_block.get_text(strip=True).replace(":", "")

            if key == "ID":
                span = block.find("span")
                if span:
                    out["meta"]["id"] = span.get_text(strip=True)
            elif key == "Released Date":
                val = block.find("span", class_="value")
                out["meta"]["release_date"] = self._get_text(val)
            elif key == "Duration":
                val = block.find("span", class_="value")
                out["meta"]["duration"] = self._get_text(val)
            elif key == "Maker":
                span = block.find("span")
                out["meta"]["maker"] = self._get_text(span)
            elif key == "Series":
                span = block.find("span")
                out["meta"]["series"] = self._get_text(span)
            elif key == "Rating":
                span = block.find("span")
                rating, users = self._parse_rating_and_reviews(self._get_text(span))
                out["meta"]["rating"] = rating
                out["meta"]["users_reviewed"] = users
            elif key == "Tags":
                for tag in block.find_all("a"):
                    text = tag.get_text(strip=True)
                    if text:
                        out["tags"].append(text)
            elif key == "Actor(s)":
                for actor in block.find_all("span", class_="value"):
                    name = actor.a.get_text(strip=True) if actor and actor.a else "Unknown"
                    gender = "female" if actor.find("strong", class_="symbol female") else "male"
                    out["actors"].append({"name": name, "gender": gender})

    def _parse_cover_and_previews(self, soup: BeautifulSoup, out: dict[str, Any]) -> None:
        cover_image_div = soup.find("div", class_="column video-cover")
        if cover_image_div:
            cover_link = cover_image_div.find("a")
            if cover_link and cover_link.has_attr("href"):
                out["cover_image"] = cover_link["href"]

        preview_images = soup.find("div", class_="preview-images")
        if preview_images:
            for a in preview_images.find_all("a"):
                href = self._get_attr(a, "href")
                if href:
                    out["preview_images"].append(href)

    def _parse_magnet_links(self, soup: BeautifulSoup, out: dict[str, Any]) -> None:
        magnet_links_section = soup.find("div", id="magnets")
        if not magnet_links_section:
            return

        for item in magnet_links_section.find_all("div", class_="item"):
            name_tag = item.find("span", class_="name")
            a_tag = item.find("a")
            size_tag = item.find("span", class_="meta")

            link_name = self._get_text(name_tag)
            link = self._get_attr(a_tag, "href")
            size_info = self._get_text(size_tag)

            # Keep keys consistent with existing behavior
            out["magnet_links"].append({
                "name": link_name,
                "link": link,
                "size": size_info,
            })

    @staticmethod
    def _parse_rating_and_reviews(text: str | None) -> tuple[str | None, str | None]:
        """Split rating text like "⭐️⭐️⭐️⭐️⭐️, 100 reviews".

        Returns (rating_str, users_reviewed_str). If parsing fails, returns
        (rating_part_or_None, None) to mirror previous behavior tolerantly.
        """
        if not text:
            return None, None
        parts = [p.strip() for p in text.split(",")]
        rating = parts[0] if parts else None
        users: str | None = None
        if len(parts) > 1:
            # Expect formats like "100 reviews"; take the numeric token.
            tokens = parts[1].split()
            if len(tokens) >= 2:
                users = tokens[-2]
        return rating, users
