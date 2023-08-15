from prometheus_client import Counter, Gauge

class Metrics(object):
    def __init__(self):
        self.counter__requests__photo_page = Counter('photo_requests', 'Number of photo page requests')
        self.counter__error__404 = Counter('404_counter', 'Number of 404 page returned')
        self.gauge__icloud__token_exparation_seconds = Gauge("icloud_token_exparation_seconds", "Number of seconds till icloud 2fa token expires")
        self.gauge__icloud__token_exparation_epoch = Gauge("icloud_token_exparation_epoch", "Epoch of of when icloud 2fa token expires")
