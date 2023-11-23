from prometheus_client import Counter, Gauge, Enum

class Metrics(object):
    def __init__(self):
        self.counter__requests__photo_page = Counter('page_photo_requests', 'Number of photo page requests')
        self.counter__error__404 = Counter('page_error_404_counter', 'Number of 404 page returned')
        
        self.gauge__icloud__token_exparation_epoch = Gauge("icloud_token_exparation_epoch", "Epoch of when icloud 2fa token expires")
        self.gauge__icloud__next_sync_epoch = Gauge("icloud_next_sync_epoch", "Epoch of the next sync", ["SyncName"])
        self.gauge__icloud__last_sync_epoch = Gauge("icloud_last_sync_epoch", "Epoch of the last sync", ["SyncName"])
        self.gauge__icloud__last_sync_elapse_time = Gauge("icloud_sync_elapse_time", "Number of seconds the sync took", ["SyncName"])

        self.enum__icloud__sync_running_status = Enum("icloud_sync_running_status", "Current sync running status", ["SyncName"], states=['running', 'waiting'])

        self.counter__icloud__number_of_files_downloaded = Counter("icloud_number_of_files_downloaded", "Number of files the sync downloaded")
        self.counter__icloud__download_errors = Counter("icloud_download_errors", "Number of download errors encountered")
        self.counter__icloud__errors = Counter("icloud_errors", "Number of errors encountered")
