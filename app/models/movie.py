class MovieListItem:
    def __init__(self, id: str=None, title: str=None, cover: str=None, link: str=None, score: str=None, meta: str=None):
        self.id = id
        self.title = title
        self.cover = cover
        self.link = link
        self.score = score
        self.meta = meta

    def __eq__(self, other):
        if not isinstance(other, MovieListItem):
            return NotImplemented
        return self.id == other.id

    def __repr__(self):
        return f"MovieListItem(id={self.id}, title={self.title}, score={self.score}, meta={self.meta}, cover={self.cover}, link={self.link})"
