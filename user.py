import threading
import requests
from bs4 import BeautifulSoup
from movie import Movie
from session import Session


class User:
    # todo implement watchlist
    # todo implement get diary
    # todo implement get list
    # todo add movie to list
    # todo create new list

    # todo recent activity
    # todo watched films
    # todo films this year
    # todo lists
    # todo following
    # todo followers
    # todo bio
    # todo diary
    # todo ratings
    # todo tags
    # todo reviews
    # todo watchlist
    # todo lists
    # todo likes
    # todo stats

    def __init__(self, username):
        self._username = username

    def load_detail(self):
        session = Session()
        url = f'https://letterboxd.com/{self._username}'

        headers = session.build_headers()
        response = requests.get(url, headers=headers)

        self._parse_html(response.text)

    def _parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        self.favorite_films = self._extract_favorite_films(soup)
        thread_load_favs_details = threading.Thread(target=self.load_favorites_details_async())
        thread_load_favs_details.start()

        thread_load_favs_details.join()

    def _extract_favorite_films(self, soup):
        favorite_films = []

        favorites_section = soup.find('section', {'id': 'favourites'})
        favorite_items = favorites_section.find_all('li', {'class': 'poster-container favourite-film-poster-container'})

        for item in favorite_items:
            film_slug = item.find('div', {'class': 'really-lazy-load'})['data-film-slug']

            film = Movie(f'/film/{film_slug}')
            favorite_films.append(film)

        return favorite_films

    def load_favorites_details_async(self):
        for film in self.favorite_films:
            film.load_detail()

