import json
import re
import requests
import demjson3
from bs4 import BeautifulSoup
from letterboxd_apy.actor import Actor
from letterboxd_apy.crew import Crew
from letterboxd_apy.session import Session
from letterboxd_apy.release import Release


# todo implement releases
# todo test tags
# todo test multilined reviews
# todo implement to get all reviews
# todo implement to get all fans - or at least the count
# todo implement delete diary entry
# todo implement own rating


class Movie:
    def __init__(self, link, title='', year=-1):
        self._link = link
        self._title = title
        self._year = year
        self._runtime = -1

    def load_detail(self):  # async?
        url = f'https://letterboxd.com{self._link}'
        session = Session()

        response = requests.get(url, headers=session.build_headers(), cookies=session.cookies)
        return self._parse_html(response.text)

    def _parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        self._extract_film_info(soup)
        tagline_element = soup.find('h4', class_='tagline')
        if tagline_element:
            self._tagline = tagline_element.text
        else:
            self._tagline = None
        self._summary = soup.find('div', class_='truncate').find('p').text
        self._film_id = self._extract_film_id(soup)
        self._cast = self._extract_cast(soup)
        self._crew = self._extract_crew(soup)
        self._details = self._extract_detail(soup)
        self._genres = self._extract_genres(soup)
        self._releases = self._extract_releases(soup)
        self._extract_ratings(soup)

    def _extract_film_info(self, soup):
        script_tags = soup.find_all('script')

        for script in script_tags:
            script_text = script.get_text()
            match = re.search(r'var filmData = ({.*?});', script_text)
            if match:
                film_data_json = match.group(1)
                film_data = self._convert_to_json(film_data_json)

                self._title = film_data['name']
                self._year = film_data['releaseYear']
                self._link = film_data['path']
                self._runtime = film_data['runTime']
                return

    def _convert_to_json(self, input_str):
        data = demjson3.decode(input_str)
        return data
        # json_str = re.sub(r'(\w+):', r'"\1":', input_str)
        # json_str = re.sub(r',(\s*})', r'\1', json_str)
        # json_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2":', input_str)
        # json_str = re.sub(r'([^"])[:]', r'\1":', json_str)
        # json_str = json_str.replace("\\'", "'")
        #
        # try:
        #     return json.loads(json_str)
        # except json.JSONDecodeError:
        #     pass

    def _extract_film_id(self, soup):
        poster_div = soup.find('div', class_='film-poster')
        film_id = poster_div['data-film-id']
        return film_id

    def _extract_cast(self, soup):
        cast_container = soup.find('div', id='tab-cast')
        cast_links = cast_container.find_all('a', class_='text-slug tooltip')
        # cast = [link.text for link in cast_links]

        cast = []
        for link in cast_links:
            actor = Actor(link.text)
            cast.append(actor)

        return cast

    def _extract_crew(self, soup):
        crew_container = soup.find('div', id='tab-crew')
        crew = []

        for h3 in crew_container.find_all('h3'):
            crew_role = h3.find('span', class_='crewrole -full').text
            crew_names = [a.text for a in h3.find_next('p').find_all('a')]

            for crew_name in crew_names:
                crew_member = Crew(crew_name, crew_role)
                crew.append(crew_member)

        return crew

    def _extract_detail(self, soup):
        # todo - maybe create proper classes for this
        details = {}

        tab_details = soup.find('div', {'id': 'tab-details'})

        if tab_details:
            categories = tab_details.find_all('h3')
            for category in categories:
                category_name = category.find('span').text
                if category_name == 'Alternative Titles':
                    alternative_titles = category.find_next('div', {'class': 'text-indentedlist'}).find(
                        'p').text.strip().split(', ')
                    details[category_name] = alternative_titles
                else:
                    items = category.find_next('div').find_all('a', {'class': 'text-slug'})
                    item_names = [item.text for item in items]
                    details[category_name] = item_names

        return details

    def _extract_genres(self, soup):
        tab_genres = soup.find('div', {'id': 'tab-genres'})

        if tab_genres:
            h3 = tab_genres.find('h3')
            if h3 and h3.find('span').text == 'Genres':
                genre_links = tab_genres.find_all('a', {'class': 'text-slug'})
                genres = [link.text for link in genre_links]
                return genres

        return None

    def _extract_releases(self, soup):
        # todo - implement
        return

        # releases = []
        #
        # release_sections = soup.find_all('div', class_='release-table -bydate')
        #
        # for section in release_sections:
        #     release_title = section.find_previous('h3',class_='release-table-title')
        #     release_type = release_title.text.strip()
        #
        #     countries = section.find_all('span', class_='name')
        #     countries = [country.text.strip() for country in countries]
        #     dates = section.find_all('h5', class_='date')
        #     dates = [date.text.strip() for date in dates]
        #
        #     for country, date in zip(countries, dates):
        #         release = Release(release_type, country, date)
        #         releases.append(release)
        #
        # return releases

        release_info = soup.find_all('div', class_='release-table -bycountry')
        release_data = []

        for info in release_info:
            countries = info.find_all('span', class_='name')
            dates = info.find_all('h6', class_='date')
            certifications = info.find_all('span', class_='release-certification-badge')
            types = info.find_all('span', class_='type')
            notes = info.find_all('span', class_='release-note')

            for country, date, cert, release_type, note in zip(countries, dates, certifications, types, notes):
                country = country.text.strip()
                date = date.text.strip()
                certification = cert.text.strip() if cert else None
                release_type = release_type.text.strip()
                note = note.text.strip() if note else None

                release = {
                    'Country': country,
                    'Date': date,
                    'Certification': certification,
                    'Release Type': release_type,
                    'Note': note
                }

                release_data.append(release)

        return release_data

    def _extract_ratings(self, soup):
        json_script = soup.find('script', {'type': 'application/ld+json'}).string
        json_script = json_script.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
        data = json.loads(json_script)

        self.rating = data['aggregateRating']['ratingValue']
        self.best_rating = data['aggregateRating']['bestRating']
        self.worst_rating = data['aggregateRating']['worstRating']
        self.total_rating_count = data['aggregateRating']['ratingCount']
        self.total_review_count = data['aggregateRating']['reviewCount']
        self.total_rating_count = data['aggregateRating']['ratingCount']

    def log(self, rating=0, date=None, rewatch=False, liked=False, review=None, tags=None):
        """
        This will create a log in the diary of the logged-in user.

        :param rating: The rating to save in the diary. 0 = Zero stars, 10 = Five stars
        :param date: The date when the film was watched in the format: yyyy-MM-dd
        :param rewatch: True if the film was watched before
        :param liked: True if the liked (heart) icon should be checked
        :param review: If a text is given, it will be saved as a review
        :param tags: If a tag is given, it will get added to the diary
        :return: Returns true if the film was logged
        """

        if -1 < rating > 10:
            raise Exception('invalid rating')

        url = 'https://letterboxd.com/s/save-diary-entry'

        session = Session()
        headers = session.build_headers()

        data = {
            "__csrf": session.csrf,
            "viewingId": "",
            "filmId": self._film_id,
            "specifiedDate": 'true' if date else 'false',
            "rewatch": 'true' if rewatch else 'false',
            "viewingDateStr": date or '',
            "review": review or '',
            "tags": tags or '',
            "liked": 'true' if liked else 'false',
            "rating": rating
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            print("logged movie")
            return True

        return False

    def __repr__(self):
        if self.title and self.year:
            return f'{self._title} ({self.year})]'

        return self._link

    @property
    def title(self):
        return self._title

    @property
    def year(self):
        return self._year

    @property
    def link(self):
        return self._link

    @property
    def runtime(self):
        return self._runtime

    @property
    def tagline(self):
        return self._tagline

    @property
    def summary(self):
        return self._summary

    @property
    def film_id(self):
        return self._film_id

    @property
    def cast(self):
        return self._cast

    @property
    def crew(self):
        return self._crew

    @property
    def details(self):
        return self._details

    @property
    def genres(self):
        return self._genres

    @property
    def releases(self):
        return self._releases
