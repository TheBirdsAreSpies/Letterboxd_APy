import concurrent
import requests
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from bs4 import BeautifulSoup
from letterboxd_apy.movie import Movie
from letterboxd_apy.session import Session


class Visibility(Enum):
    PUBLIC = 0
    ANYONE_SHARED_LINK = 1
    FRIENDS_SHARED_LINK = 2
    PRIVATE = 3


class List:
    def __init__(self, title, slug, visibility):
        self.title = title
        self.slug = slug
        self.visibility = self._get_visibility_from_str(visibility)

    def load_items(self, deep_load=False, max_threads=3):
        session = Session()
        url = f'https://letterboxd.com{self.slug}'
        headers = session.build_headers()

        movies = []
        page = 1
        next_page = True

        while next_page:
            response = requests.get(f'{url}/page/{page}/', headers=headers)
            if response.status_code == 200:
                extracted_data = self.extract_movie_info(response.content, deep_load, max_threads)
                if not extracted_data:
                    next_page = False
                else:
                    movies.extend(extracted_data)
                    page += 1
            else:
                next_page = False

        return movies

    def extract_movie_info(self, html, deep_load, max_threads):
        soup = BeautifulSoup(html, 'html.parser')

        movies = []
        movie_elements = soup.find_all('li', class_='poster-container')

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            for movie_element in movie_elements:
                title = movie_element.find('img')['alt']
                link = movie_element.find('div', class_='linked-film-poster')['data-target-link']
                # user_rating = movie_element['data-owner-rating'] # todo not used yet

                movie = Movie(link, title)
                movies.append(movie)

                if deep_load:
                    executor.submit(movie.load_detail)

            executor.shutdown(True)

        return movies

    def _get_visibility_from_str(self, visibility: str) -> Visibility:
        if visibility == 'Visible to friends (people you follow) with share link':
            return Visibility.FRIENDS_SHARED_LINK
        elif visibility == 'Visible to you — private list':
            return Visibility.PRIVATE
        elif visibility == 'Visible to anyone with share link':
            return Visibility.ANYONE_SHARED_LINK
        else:
            return Visibility.PUBLIC

    def _get_str_from_visibility(self):
        if self.visibility == Visibility.PUBLIC:
            return 'Public'
        elif self.visibility == Visibility.PRIVATE:
            return 'Private'
        elif self.visibility == Visibility.ANYONE_SHARED_LINK:
            return 'Anyone with shared link'
        elif self.visibility == Visibility.FRIENDS_SHARED_LINK:
            return 'Friends with shared link'

    def __repr__(self):
        return f'{self.title} ({self._get_str_from_visibility()})'