class Session:
    def __init__(self, csrf, cookies):
        self._csrf = csrf
        self.cookies = cookies

    @property
    def csrf(self):
        return self._csrf

    @csrf.setter
    def csrf(self, csrf):
        self._csrf = csrf

    def build_headers(self):
        # we have to build a cookies string because setting the param per request does not work somehow
        cookies = f'com.xk72.webparts.csrf={self.csrf};'
        for cookie in self.cookies:
            cookies = cookies + f'{cookie.name}={cookie.value}; '

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Accept": "*/*",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://letterboxd.com/",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://letterboxd.com",
            "Cookie": cookies
        }

        return headers
