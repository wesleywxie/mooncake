from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, String, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (UniqueConstraint("code", name="uq_movie_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Title section
    code: Mapped[str | None] = mapped_column(String(64), nullable=True)  # title.id
    current_title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Meta section
    release_date: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration: Mapped[str | None] = mapped_column(String(64), nullable=True)
    maker: Mapped[str | None] = mapped_column(String(128), nullable=True)
    series: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rating_text: Mapped[str | None] = mapped_column(String(64), nullable=True)
    users_reviewed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    want_to_watch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    watched: Mapped[int | None] = mapped_column(Integer, nullable=True)

    cover_image: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    preview_images: Mapped[list[PreviewImage]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    tags: Mapped[list[MovieTag]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    magnets: Mapped[list[MagnetLink]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )
    actor_links: Mapped[list[MovieActor]] = relationship(
        back_populates="movie", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - repr not critical
        return f"<Movie id={self.id} code={self.code} title={self.current_title!r}>"


class PreviewImage(Base):
    __tablename__ = "movie_preview_images"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)

    movie: Mapped[Movie] = relationship(back_populates="preview_images")


class MovieTag(Base):
    __tablename__ = "movie_tags"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    tag: Mapped[str] = mapped_column(String(128), nullable=False)

    movie: Mapped[Movie] = relationship(back_populates="tags")


class Actor(Base):
    __tablename__ = "actors"
    __table_args__ = (UniqueConstraint("name", "gender", name="uq_actor_name_gender"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)

    movie_links: Mapped[list[MovieActor]] = relationship(
        back_populates="actor", cascade="all, delete-orphan"
    )


class MovieActor(Base):
    __tablename__ = "movie_actors"
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actors.id"), primary_key=True)

    movie: Mapped[Movie] = relationship(back_populates="actor_links")
    actor: Mapped[Actor] = relationship(back_populates="movie_links")


class MagnetLink(Base):
    __tablename__ = "movie_magnets"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    link: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    size: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Heuristic selection: mark if this magnet looks like a perfect 1080p match
    perfect_match: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    movie: Mapped[Movie] = relationship(back_populates="magnets")
