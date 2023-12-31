import requests
import re
import json
from letterboxd_apy.credentials import Credentials
from letterboxd_apy.session import Session


class Login:
    LOGIN_URL = "https://letterboxd.com/user/login.do"

    def __init__(self, username: str, password: str):
        if username is None or password is None:
            raise Exception("Username or password not set.")

        self.credentials = Credentials(username, password)
        self.is_logged_in = False

    def sign_in(self) -> Session:
        # perform a request to extract csrf token
        response = requests.get(self.LOGIN_URL)
        csrf_pattern = re.compile(r'"csrf":\s*"([^"]+)"')
        match = csrf_pattern.search(response.text)

        if match:
            csrf_token = match.group(1)
            self.credentials.csrf = csrf_token
        else:
            raise Exception("was not able to extract csrf token")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/118.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://letterboxd.com",
            "Referer": "https://letterboxd.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "de,en-US;q=0.9,en;q=0.8,de-DE;q=0.7,sr;q=0.6,ko;q=0.5",
            "Cookie": f"com.xk72.webparts.csrf={csrf_token};"
        }

        data = {
            "__csrf": csrf_token,
            "authenticationCode": "",
            "username": self.credentials.username,
            "password": self.credentials.password,
            "remember": True
        }

        response = requests.post(self.LOGIN_URL, headers=headers, data=data)

        if response.status_code == 200:
            response_data = json.loads(response.text)
            self.is_logged_in = response_data['result'] == 'success'

            session = Session(csrf_token, response.cookies)
            return session

        raise Exception('was not able to create a session')

    def download_export_data(self, file_name='letterboxd_export.zip'):
        session = Session()
        url = 'https://letterboxd.com/data/export/'

        if not self.is_logged_in:
            raise Exception('You have to log in to download your export data.')

        try:
            headers = session.build_headers()
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.content
                if 'html' in str(data):
                    raise Exception('User not signed in')

                with open(file_name, 'wb') as file:
                    file.write(data)
            else:
                print("Error while downloading data")

        except requests.exceptions.RequestException as e:
            print(f"Unable to get web request: {e}")
