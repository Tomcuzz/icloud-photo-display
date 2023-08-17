from prometheus_client import Counter, Gauge

class Metrics(object):
    def __init__(self):
        self.counter__requests__photo_page = Counter('photo_requests', 'Number of photo page requests')
        self.counter__error__404 = Counter('404_counter', 'Number of 404 page returned')
        self.gauge__icloud__token_exparation_seconds = Gauge("icloud_token_exparation_seconds", "Number of seconds till icloud 2fa token expires")
        self.gauge__icloud__token_exparation_epoch = Gauge("icloud_token_exparation_epoch", "Epoch of when icloud 2fa token expires")

        self.gauge__icloud__last_sync_seconds = Gauge("icloud_last_sync_seconds", "Number of seconds since the last sync")
        self.gauge__icloud__tlast_sync_epoch = Gauge("icloud_last_sync_epoch", "Epoch since the last sync")

        self.gauge__icloud__last_sync_elapse_time = Gauge("icloud_last_sync_elapse_time", "Number of seconds the last sync took")
        self.counter__icloud__number_of_files_downloaded = Counter("icloud_number_of_files_downloaded", "Number of files the sync downloaded")
        self.counter__icloud__download_errors = Counter("icloud_download_errors", "Number of download errors encountered")
        self.counter__icloud__errors = Counter("icloud_errors", "Number of errors encountered")
