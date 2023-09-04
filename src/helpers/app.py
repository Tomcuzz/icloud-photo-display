""" Code to run icloud photo display """
from src.helpers.metrics import Metrics
from src.helpers.settings import Settings
from src.helpers.icloud import ICloud
from src.helpers.sync_thread import SyncHandler

class AppHelper(object):
    def __init__(self):
        self.prom_metrics = Metrics()
        self.configs = Settings("/icloudpd", "configs.json")
        self.icloud_helper = ICloud(self.configs, self.prom_metrics)
        self.sync_handler = SyncHandler(self.configs, self.icloud_helper)
    
    def renew_icloud(self):
        self.icloud_helper = ICloud(self.configs, self.prom_metrics)