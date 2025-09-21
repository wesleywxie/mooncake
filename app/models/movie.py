class MovieListItem:
    def __init__(self, title: str=None, cover: str=None, link: str=None, score: str=None, meta: str=None):
        self.title = title
        self.cover = cover
        self.link = link
        self.score = score
        self.meta = meta

    def __eq__(self, other):
        if not isinstance(other, MovieListItem):
            return NotImplemented
        return (self.title, self.score, self.meta, self.cover, self.link) == \
            (other.title, other.score, other.meta, other.cover, other.link)

    def __repr__(self):
        return f"MovieListItem(title={self.title}, score={self.score}, meta={self.meta}, cover={self.cover}, link={self.link})"
