import requests
from bs4 import BeautifulSoup

from letterboxd_apy.session import Session
from movie import Movie
from enum import Enum


class SearchType(Enum):
    FILMS = 1
    # REVIEWS = 2
    # LISTS = 3
    # ORIGINAL_LISTS = 4
    # STORIES = 5
    # CAST_CREW_STUDIOS = 6
    # MEMBERS = 7
    # TAGS = 8
    # ARTICLES = 9
    # PODCAST_EPISODES = 10


class Search:
    SEARCH_URL = 'https://letterboxd.com/search/__SEARCH_STRING__/?adult'

    def search(self, query: str, search_type: SearchType):
        query = query.replace(' ', '+')
        url = self.SEARCH_URL.replace('__SEARCH_STRING__', query)

        session = Session()
        headers = session.build_headers()

        response = requests.get(url, headers=headers)

        search_cases = {
            SearchType.FILMS: self._parse_html_films
        }

        case = search_cases.get(search_type)
        return case(response.text)

    def _parse_html_films(self, html_code):
        soup = BeautifulSoup(html_code, 'html.parser')
        ul_element = soup.find('ul', class_='results')
        li_elements = ul_element.find_all('li')
        movie_objects = []
        for li in li_elements:
            title = li.find('a', href=True)
            if title and '/film/' in title['href']:
                year_element = li.find('small', class_='metadata')
                year = year_element.text.strip() if year_element else None
                title_text = title.text.strip()
                title_text = title_text if not year else title_text.replace(year, '').strip()
                director_element = li.find('a', class_='text-slug')
                director = director_element.text.strip() if director_element else None

                movie = Movie(title['href'], title_text, year)
                movie_objects.append(movie)

        return movie_objects
