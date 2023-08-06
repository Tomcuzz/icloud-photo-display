from prometheus_client import Counter

class Metrics(object):
    def __init__(self):
        self.photo_requests_counter = Counter('photo_requests', 'Number of photo page requests')