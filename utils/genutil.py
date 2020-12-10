


class Mapping(dict):

    def __init__(self, desc: dict):
        self.update(desc)

    def __getattr__(self, attr):
        return self.get(attr)


class n:

    def __init__(self, n):
        pass
