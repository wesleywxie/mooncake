from __future__ import annotations

from typing import Any
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie_orm import (
    Actor,
    MagnetLink,
    Movie,
    MovieActor,
    MovieTag,
    PreviewImage,
)
from app.models.movie import MovieListItem


class MovieRepository:
    """Persistence helpers for movie list items (legacy)."""

    def __init__(self, session: Session):
        self.session = session

    def upsert_from_list_item(self, item: MovieListItem) -> Movie:
        # Legacy no-op mapping retained for compatibility; stores minimal data in Movie.
        movie: Movie | None = None

        if item.id:
            movie = self.session.scalar(select(Movie).where(Movie.code == item.id))

        if movie is None:
            movie = Movie()
            self.session.add(movie)

        movie.code = item.id
        movie.current_title = item.title
        movie.cover_image = item.cover
        return movie

    def upsert_many(self, items: Iterable[MovieListItem]) -> list[Movie]:
        return [self.upsert_from_list_item(i) for i in items]


class MovieDetailsRepository:
    """Persist full movie details extracted by DataExtractor.extract_movie_details."""

    def __init__(self, session: Session):
        self.session = session

    # -------------------
    # Public API
    # -------------------
    def upsert_from_details(self, details: dict[str, Any]) -> Movie:
        movie = self._find_or_create_movie(details)
        self._update_scalar_fields(movie, details)
        self._sync_tags(movie, details.get("tags", []))
        self._sync_preview_images(movie, details.get("preview_images", []))
        self._sync_magnets(movie, details.get("magnet_links", []))
        self._sync_actors(movie, details.get("actors", []))
        # After syncing magnets, determine the best (likely 1080p) match
        self._select_perfect_magnet(movie)
        return movie

    # -------------------
    # Internals
    # -------------------
    def _find_or_create_movie(self, details: dict[str, Any]) -> Movie:
        title_info = details.get("title", {}) or {}
        code = title_info.get("id")
        current_title = title_info.get("current_title")
        maker = (details.get("meta", {}) or {}).get("maker")

        movie: Movie | None = None
        if code:
            movie = self.session.scalar(select(Movie).where(Movie.code == code))
        if movie is None and current_title and maker:
            movie = self.session.scalar(
                select(Movie).where(
                    Movie.current_title == current_title, Movie.maker == maker
                )
            )
        if movie is None:
            movie = Movie()
            self.session.add(movie)
        return movie

    def _update_scalar_fields(self, movie: Movie, details: dict[str, Any]) -> None:
        title_info = details.get("title", {}) or {}
        meta = details.get("meta", {}) or {}

        movie.code = title_info.get("id")
        movie.current_title = title_info.get("current_title")

        movie.release_date = meta.get("release_date")
        movie.duration = meta.get("duration")
        movie.maker = meta.get("maker")
        movie.series = meta.get("series")
        movie.rating_text = meta.get("rating")
        movie.cover_image = details.get("cover_image")

        movie.users_reviewed = _to_int(meta.get("users_reviewed"))
        movie.want_to_watch = _to_int(meta.get("want_to_watch"))
        movie.watched = _to_int(meta.get("watched"))

    def _sync_tags(self, movie: Movie, tags: Iterable[str]) -> None:
        current = {t.tag: t for t in movie.tags}
        desired = set(t for t in tags if t)
        # Remove
        for tag_val, obj in list(current.items()):
            if tag_val not in desired:
                self.session.delete(obj)
                movie.tags.remove(obj)
        # Add
        for tag_val in desired:
            if tag_val not in current:
                movie.tags.append(MovieTag(tag=tag_val))

    def _sync_preview_images(self, movie: Movie, urls: Iterable[str]) -> None:
        current = {pi.url: pi for pi in movie.preview_images}
        desired = set(u for u in urls if u)
        for url, obj in list(current.items()):
            if url not in desired:
                self.session.delete(obj)
        for url in desired:
            if url not in current:
                movie.preview_images.append(PreviewImage(url=url))

    def _sync_magnets(self, movie: Movie, magnets: Iterable[dict[str, Any]]) -> None:
        # Deduplicate magnets by link when present; otherwise by (name, size)
        def key(m: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
            return (m.get("link"), m.get("name"), m.get("size"))

        current = {
            key({"link": m.link, "name": m.name, "size": m.size}): m
            for m in movie.magnets
        }
        desired_input = [m for m in magnets if m]
        desired = {key(m): m for m in desired_input}

        for k, obj in list(current.items()):
            if k not in desired:
                self.session.delete(obj)
        for k, val in desired.items():
            if k not in current:
                movie.magnets.append(
                    MagnetLink(
                        name=val.get("name"), link=val.get("link"), size=val.get("size")
                    )
                )

    def _select_perfect_magnet(self, movie: Movie) -> None:
        """Mark exactly one magnet as perfect_match when possible."""

        minutes = _parse_minutes(movie.duration)
        if minutes is None or minutes <= 0 or not movie.magnets:
            # Clear flags if unknown
            for magnet in movie.magnets:
                if magnet.perfect_match:
                    magnet.perfect_match = False
            return

        target_mb_per_min = 55.0  # ~7.3 Mbps
        min_mb_per_min = 35.0
        max_mb_per_min = 80.0

        best: MagnetLink | None = None
        best_score = float("inf")

        for magnet in movie.magnets:
            size_mb = _parse_size_mb(magnet.size)
            if size_mb is None:
                continue
            mb_per_min = size_mb / float(minutes)
            in_band = min_mb_per_min <= mb_per_min <= max_mb_per_min
            name_hint = _looks_like_1080p_name(magnet.name)
            # Scoring: prioritize name hints and closeness to target when in band
            band_penalty = 0.0 if in_band else 1.0
            name_bonus = -0.25 if name_hint else 0.0
            distance = abs(mb_per_min - target_mb_per_min) / target_mb_per_min
            score = band_penalty + distance + name_bonus
            if score < best_score:
                best_score = score
                best = magnet

        if best is None:
            for magnet in movie.magnets:
                if magnet.perfect_match:
                    magnet.perfect_match = False
            return

        for magnet in movie.magnets:
            magnet.perfect_match = magnet is best

    def _sync_actors(self, movie: Movie, actors: Iterable[dict[str, Any]]) -> None:
        # Current associations
        current = {
            (link.actor.name, link.actor.gender): link for link in movie.actor_links
        }
        desired_keys = set()

        for item in actors:
            if not item:
                continue
            name = item.get("name")
            gender = item.get("gender")
            if not name:
                continue
            key = (name, gender)
            desired_keys.add(key)
            if key in current:
                continue
            actor = self.session.scalar(
                select(Actor).where(Actor.name == name, Actor.gender == gender)
            )
            if actor is None:
                actor = Actor(name=name, gender=gender)
                self.session.add(actor)
                self.session.flush()  # ensure PK for association
            movie.actor_links.append(MovieActor(actor=actor))

        # Remove stale links
        for key, link in list(current.items()):
            if key not in desired_keys:
                self.session.delete(link)


def _to_int(val: Any) -> int | None:
    try:
        if val is None:
            return None
        return int(str(val).strip())
    except (TypeError, ValueError):
        return None


# -------------------
# Heuristics for selecting perfect magnet
# -------------------


def _parse_minutes(duration: str | None) -> int | None:
    if not duration:
        return None
    try:
        # Expected like "120 min" or "120min" or "120"
        s = (
            str(duration)
            .strip()
            .lower()
            .replace("minutes", "min")
            .replace("minute(s)", "min")
        )
        num = "".join(ch for ch in s if ch.isdigit() or ch == ".")
        if not num:
            return None
        return int(float(num))
    except Exception:
        return None


def _parse_size_mb(size: str | None) -> float | None:
    if not size:
        return None
    s = str(size).strip().upper().replace(" ", "")
    # Accept forms like 1.2GB, 900MB, 700KB
    import re

    m = re.match(r"([0-9]+(?:\.[0-9]+)?)(KB|MB|GB)", s)
    if not m:
        # Try relaxed: keep first number and unit separated by spaces
        s2 = str(size).strip().upper()
        m = re.match(r"([0-9]+(?:\.[0-9]+)?)\s*(KB|MB|GB)", s2)
        if not m:
            return None
    val = float(m.group(1))
    unit = m.group(2)
    if unit == "KB":
        return val / 1024.0
    if unit == "MB":
        return val
    if unit == "GB":
        return val * 1024.0
    return None


def _looks_like_1080p_name(name: str | None) -> bool:
    if not name:
        return False
    n = name.lower()
    hints = ("1080", "1080p", "fhd", "fullhd")
    return any(h in n for h in hints)
