import json
import unittest

from sqlalchemy.orm import Session

from app.db import Base, get_engine, get_session_maker
from app.models.movie_orm import Movie, MagnetLink
from app.services.repository import MovieDetailsRepository


class TestMagnetHeuristicsFromExamples(unittest.TestCase):
    def setUp(self):
        self.engine = get_engine("sqlite+pysqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        SessionLocal = get_session_maker(self.engine)
        self.session: Session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def _load_example(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _persist_and_fetch(self, details: dict) -> Movie:
        repo = MovieDetailsRepository(self.session)
        movie = repo.upsert_from_details(details)
        self.session.commit()
        return self.session.get(Movie, movie.id)

    def _assert_single_perfect(self, movie: Movie) -> MagnetLink:
        perfects = [m for m in movie.magnets if m.perfect_match]
        self.assertEqual(len(perfects), 1, "Exactly one magnet should be marked perfect_match")
        return perfects[0]

    def test_fct_183_selects_larger_within_band(self):
        details = self._load_example("examples/FCT-183.json")
        movie = self._persist_and_fetch(details)
        chosen = self._assert_single_perfect(movie)
        # Expect the 3.98GB option beats the 1.71GB for 90 minutes
        self.assertIn("3.98GB", (chosen.size or ""))

    def test_uta_108_prefers_closest_to_target(self):
        details = self._load_example("examples/UTA-108.json")
        movie = self._persist_and_fetch(details)
        chosen = self._assert_single_perfect(movie)
        # Both are around 5GB for 118 minutes; 5.01GB is slightly closer to target MB/min
        self.assertIn("5.01GB", (chosen.size or ""))


if __name__ == "__main__":
    unittest.main()
