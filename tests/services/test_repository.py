import unittest

from sqlalchemy.orm import Session

from app.db import Base, get_engine, get_session_maker
from app.models.movie_orm import Movie, MovieTag, PreviewImage, MagnetLink, Actor, MovieActor
from app.services.repository import MovieDetailsRepository


class TestMovieDetailsRepository(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for hermetic tests
        self.engine = get_engine("sqlite+pysqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        SessionLocal = get_session_maker(self.engine)
        self.session: Session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def test_save_full_details_and_update(self):
        repo = MovieDetailsRepository(self.session)
        details = {
            "title": {"id": "ID123", "current_title": "Movie Title"},
            "meta": {
                "release_date": "2023-01-01",
                "duration": "120 min",
                "maker": "Studio A",
                "series": "Series B",
                "rating": "⭐️⭐️⭐️⭐️⭐️",
                "users_reviewed": "100",
            },
            "tags": ["Tag1", "Tag2"],
            "actors": [{"name": "Actor1", "gender": "female"}],
            "cover_image": "/cover.jpg",
            "preview_images": ["/img1.jpg", "/img2.jpg"],
            "magnet_links": [
                {"name": "Link1", "link": "magnet:?xt=urn:btih:abc123", "size": "1.2 GB"}
            ],
        }

        movie = repo.upsert_from_details(details)
        self.session.commit()

        m = self.session.get(Movie, movie.id)
        self.assertEqual(m.code, "ID123")
        self.assertEqual(m.current_title, "Movie Title")
        self.assertEqual(m.release_date, "2023-01-01")
        self.assertEqual(m.maker, "Studio A")
        self.assertEqual(len(m.tags), 2)
        self.assertEqual(len(m.preview_images), 2)
        self.assertEqual(len(m.magnets), 1)
        self.assertEqual(len(m.actor_links), 1)

        # Update: remove Tag2, add Tag3, change users_reviewed, add second actor
        details_update = {
            **details,
            "meta": {**details["meta"], "users_reviewed": 120},
            "tags": ["Tag1", "Tag3"],
            "actors": details["actors"] + [{"name": "Actor2", "gender": "male"}],
        }
        repo.upsert_from_details(details_update)
        self.session.commit()

        m2 = self.session.get(Movie, movie.id)
        self.assertEqual(m2.users_reviewed, 120)
        self.assertEqual(sorted(t.tag for t in m2.tags), ["Tag1", "Tag3"])
        self.assertEqual(len(m2.actor_links), 2)


if __name__ == "__main__":
    unittest.main()
