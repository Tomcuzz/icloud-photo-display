""" Code Referance all the helpers """
from flask import Flask

class AppHelper(object):
    def __init__(self, flask_app:Flask):
        from src.helpers.metrics import Metrics
        from src.helpers.settings import Settings
        from src.helpers.icloud import ICloud
        from src.helpers.sync_thread import SyncHandler
        self.flask_app = flask_app
        self.prom_metrics = Metrics()
        self.configs = Settings("/icloudpd", "configs.json")
        self.icloud_helper = ICloud(self)
        self.sync_handler = SyncHandler(self)
    
    def renew_icloud(self):
        from src.helpers.icloud import ICloud
        self.icloud_helper = ICloud(self)