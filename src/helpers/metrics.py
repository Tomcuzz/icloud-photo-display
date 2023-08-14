from prometheus_client import Counter

class Metrics(object):
    def __init__(self):
        self.counter__requests__photo_page = Counter('photo_requests', 'Number of photo page requests')
        self.counter__error__404 = Counter('404_counter', 'Number of 404 page returned')