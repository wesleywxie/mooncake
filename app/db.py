from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.config import Config


class Base(DeclarativeBase):
    pass


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def get_engine(database_url: str | None = None, echo: bool | None = None) -> Engine:
    cfg = Config()
    url = database_url or cfg.DATABASE_URL
    # SQLite needs special connect args in some environments
    kwargs: dict[str, object] = {}
    if _is_sqlite(url):
        kwargs["connect_args"] = {"check_same_thread": False}
    if echo is None:
        echo = cfg.DEBUG
    return create_engine(url, echo=echo, future=True, **kwargs)


def get_session_maker(engine: Engine | None = None) -> sessionmaker[Session]:
    eng = engine or get_engine()
    return sessionmaker(bind=eng, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


@contextmanager
def get_session(engine: Engine | None = None) -> Iterator[Session]:
    SessionLocal = get_session_maker(engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine: Engine | None = None) -> None:
    """Create all tables for registered models.

    Import ORM model modules before calling to ensure they are registered on Base.metadata.
    """
    # Local import to avoid circulars in model modules
    from app.models.movie_orm import Movie  # noqa: F401 - register model

    eng = engine or get_engine()
    Base.metadata.create_all(eng)
