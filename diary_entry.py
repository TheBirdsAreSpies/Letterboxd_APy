class Diary_Entry:
    def __init__(self, date, title, rating, is_rewatch, is_liked, review, tags, slug, viewing_id):
        self.date = date
        self.title = title
        self.viewing_id = viewing_id
        self.rating = rating
        self.is_rewatch = is_rewatch
        self.is_liked = is_liked
        self.review = review
        self.tags = tags
        self.slug = slug
