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
                select(Movie).where(Movie.current_title == current_title, Movie.maker == maker)
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

        current = {key({"link": m.link, "name": m.name, "size": m.size}): m for m in movie.magnets}
        desired_input = [m for m in magnets if m]
        desired = {key(m): m for m in desired_input}

        for k, obj in list(current.items()):
            if k not in desired:
                self.session.delete(obj)
        for k, val in desired.items():
            if k not in current:
                movie.magnets.append(
                    MagnetLink(name=val.get("name"), link=val.get("link"), size=val.get("size"))
                )

    def _sync_actors(self, movie: Movie, actors: Iterable[dict[str, Any]]) -> None:
        # Current associations
        current = {(link.actor.name, link.actor.gender): link for link in movie.actor_links}
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
            actor = self.session.scalar(select(Actor).where(Actor.name == name, Actor.gender == gender))
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
