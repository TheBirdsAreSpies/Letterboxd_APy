class Credentials:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._csrf = ''

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def csrf(self):
        return self._csrf

    @csrf.setter
    def csrf(self, csrf):
        self._csrf = csrf
