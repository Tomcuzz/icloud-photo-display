from time import sleep
import logging
from threading import Thread, Lock
from src.helpers.app import AppHelper # pylint: disable=import-error
from src.helpers.icloud import ICloud # pylint: disable=import-error
from src.helpers.settings import Settings # pylint: disable=import-error

class SyncHandler(object):
    def __init__(self, app:AppHelper):
        self.app = app
        self.sync_runner = SyncThread(self.app)
        self.sync_trigger = PeriodicSyncFire(self.app.configs, self)
        self.sync_trigger.start()

    def start_sync_if_not_running(self) -> bool:
        if not self.sync_runner.is_alive():
            self.sync_runner = SyncThread(self.app)
            self.sync_runner.start()
            return True
        else:
            return False
    
    def sync_running(self) -> bool:
        return self.sync_runner.is_alive()

class PeriodicSyncFire(Thread):
    def __init__(self, configs:Settings, sync_handler:SyncHandler):
        super().__init__()
        self.configs = configs
        self.sync_handler = sync_handler
    
    def run(self):
        while True:
            if int(self.configs.watch_interval) > 0:
                self.sync_handler.start_sync_if_not_running()
                sleep(int(self.configs.watch_interval))


class SyncThread(Thread):
    def __init__(self, app:AppHelper):
        super().__init__()
        self.app = app
        self.app.renew_icloud()

    def run(self):
        logging.warning("starting sync")
        self.app.icloud_helper.sync()
        logging.warning("finished sync")