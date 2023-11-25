import threading
import requests
import demjson3
from bs4 import BeautifulSoup

from diary_entry import Diary_Entry
from letterboxd_apy.list import List
from letterboxd_apy.movie import Movie
from letterboxd_apy.session import Session


class User:
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
        thread_load_favs_details = threading.Thread(target=self._load_favorites_details_async)
        thread_load_favs_details.start()

        self.biography = self._extract_biography(soup)

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

    def _load_favorites_details_async(self):
        for film in self.favorite_films:
            film.load_detail()

    def _extract_biography(self, soup):
        bio_div = soup.find('div', class_='bio js-bio')
        if bio_div:
            bio_text = bio_div.find('p').get_text(strip=True)
            return bio_text
        else:
            return None

    def _get_lists(self):
        session = Session()
        list_url = f'https://letterboxd.com/{self._username}/lists/'

        headers = session.build_headers()
        response = requests.get(list_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        lists = soup.find_all('section', class_='list -overlapped -summary')

        user_lists = []

        for lst in lists:
            title_tag = lst.find('h2', class_='title-2 title prettify')
            title = title_tag.text.split('\xa0', 1)[0].strip()
            slug = title_tag.find('a')['href']

            visibility_tag = lst.find('span', class_='label _sr-only')
            visibility = visibility_tag.text if visibility_tag else None

            the_list = List(title, slug, visibility)
            user_lists.append(the_list)

        self.lists = user_lists

    def download_export_data(self, file_name='letterboxd_export.zip'):
        session = Session()
        url = 'https://letterboxd.com/data/export/'

        try:
            headers = session.build_headers()
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.content

                with open(file_name, 'wb') as file:
                    file.write(data)
            else:
                print("Error while downloading data")

        except requests.exceptions.RequestException as e:
            print(f"Unable to get web request: {e}")

    def _load_diary_entries(self, base_url):
        film_data = []
        page = 1

        while True:
            url = f"{base_url}page/{page}/"
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                entries = soup.find_all('tr', class_='diary-entry-row')

                if not entries:
                    break

                for entry in entries:
                    a_tag = entry.select_one('span.diary-entry-edit.show-for-owner a.edit-review-button')
                    data_dict = {key[5:]: value for key, value in a_tag.attrs.items() if key.startswith('data-')}

                    date = data_dict['viewing-date']
                    film_title = entry.find('h3', class_='prettify').text.strip()
                    viewing_id = entry['data-viewing-id']
                    rating = entry.find('input', class_='rateit-field')['value']
                    rewatch = 'icon-rewatch' in entry.find('td', class_='td-rewatch')['class']
                    liked = 'icon-liked' in entry.find('td', class_='td-like')['class']
                    review = data_dict['review-text']
                    tags = demjson3.decode(entry.find('a', class_='edit-review-button')['data-tags'])
                    film_slug = entry.find('div', class_='linked-film-poster')['data-film-slug']

                    entry = Diary_Entry(date, film_title, rating, rewatch, liked, review, tags, film_slug, viewing_id)
                    film_data.append(entry)

            page += 1

        return film_data

    def get_all_diary_entries(self):
        base_url = f'https://letterboxd.com/{self._username}/films/diary/'
        return self._load_diary_entries(base_url)


    def get_diary_entries_for_month(self, year, month):
        base_url = f'https://letterboxd.com/{self._username}/films/diary/for/{year}/{month}/'
        return self._load_diary_entries(base_url)

    def get_diary_entries_for_day(self, year, month, day):
        base_url = f'https://letterboxd.com/{self._username}/films/diary/for/{year}/{month}/{day}/'
        return self._load_diary_entries(base_url)

    def __repr__(self):
        return self._username
