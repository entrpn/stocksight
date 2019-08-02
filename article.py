class Article:

    def __init__(self, headline, url):
        self.headline = headline
        self.url = url

    def __eq__(self, other):
        return self.headline == other.headline
