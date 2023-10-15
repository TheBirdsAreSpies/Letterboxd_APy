class Actor:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return self._name
