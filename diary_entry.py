from letterboxd_apy.movie import Movie


class DiaryEntry(Movie):
    def __init__(self, date, title, rating, is_rewatch, is_liked, review, tags, slug, viewing_id):
        super().__init__(slug, title)
        self.date = date
        self.viewing_id = viewing_id
        self.rating = rating
        self.is_rewatch = is_rewatch
        self.is_liked = is_liked
        self.review = review
        self.tags = tags
