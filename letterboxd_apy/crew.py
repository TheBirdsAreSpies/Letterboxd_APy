from actor import Actor


class Crew(Actor):
    def __init__(self, name, profession):
        super().__init__(name)
        self._profession = profession

    @property
    def profession(self):
        return self._profession

    def __repr__(self):
        return f'{self.name} ({self.profession})]'
