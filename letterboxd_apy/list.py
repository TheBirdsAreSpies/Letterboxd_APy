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
    def __init__(self, list_id: int, title: str, slug: str, visibility: str, share_url=''):
        self._list_id = list_id
        self.title = title
        self.slug = slug
        if slug.endswith('/'):
            self.slug = slug.rstrip('/')
        self.visibility = self._get_visibility_from_str(visibility)
        self._movies_unloaded = []
        self.movies = []

        if share_url == '' and self.visibility != Visibility.PRIVATE:
            session = Session()
            url = f'https://letterboxd.com{slug}'
            headers = session.build_headers()
            response = requests.get(url, headers=headers)

            soup = BeautifulSoup(response.content, 'html.parser')
            url_field = soup.find('input', id=f'url-field-{list_id}')
            self.share_url = url_field['value'] if url_field else None

    @classmethod
    def create_from_user_and_listname(cls, username: str, listname: str):
        listname = listname.replace(' ', '-')
        slug = f'/{username}/list/{listname}/'

        session = Session()
        url = f'https://letterboxd.com{slug}'
        headers = session.build_headers()
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('meta', property='og:title')

        like_link = soup.find('li', class_='like-link-target')
        id_str = like_link.get('data-likeable-uid')
        list_id = int(id_str.split(':')[1])

        a_element = soup.find('a', class_='js-form-action')
        privacy_value = a_element.text.strip()

        return cls(list_id, title, slug, privacy_value)

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
                extracted_data = self._extract_movie_info(response.content, deep_load, max_threads)
                if not extracted_data:
                    next_page = False
                else:
                    movies.extend(extracted_data)
                    page += 1
            else:
                next_page = False

        self._movies_unloaded = movies

    def _extract_movie_info(self, html, deep_load, max_threads):
        soup = BeautifulSoup(html, 'html.parser')

        movies = []
        movie_elements = soup.find_all('li', class_='poster-container')

        for movie_element in movie_elements:
            title = movie_element.find('img')['alt']
            link = movie_element.find('div', class_='linked-film-poster')['data-target-link']
            # user_rating = movie_element['data-owner-rating'] # todo not used yet

            movie = Movie(link, title)
            movies.append(movie)

        if deep_load:
            self.load_movie_details(max_threads)

        return movies

    def load_movie_details(self, max_threads=3):
        def load_movie_details(m):
            m.load_detail()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            for movie in self._movies_unloaded:
                executor.submit(load_movie_details, movie)
                self.movies.append(movie)

        executor.shutdown(True)
        self._movies_unloaded = []  # todo maybe put that into another function to be sure that all movies were loaded

    def _get_visibility_from_str(self, visibility: str) -> Visibility:
        match visibility:
            case 'Visible to friends (people you follow) with share link':
                return Visibility.FRIENDS_SHARED_LINK
            case 'Visible to you — private list' | 'Make this list public':
                return Visibility.PRIVATE
            case 'Visible to anyone with share link' | 'Share private link':
                return Visibility.ANYONE_SHARED_LINK
            case _:
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
