class Session:
    _instance = None
    _csrf = None
    _cookies = None

    def __new__(cls, csrf=None, cookies=None):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
            cls._instance.init_session(csrf, cookies)
        return cls._instance

    def init_session(self, csrf, cookies):
        self.csrf = csrf
        self.cookies = cookies

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

    @property
    def csrf(self):
        return self._csrf

    @csrf.setter
    def csrf(self, csrf):
        self._csrf = csrf

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        self._cookies = cookies
