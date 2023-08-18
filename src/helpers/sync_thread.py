from time import sleep
import logging
from threading import Thread, Lock
from src.helpers.icloud import ICloud # pylint: disable=import-error
from src.helpers.settings import Settings # pylint: disable=import-error

class SyncHandler(object):
    def __init__(self, configs:Settings, icloud:ICloud):
        self.sync_runner = SyncThread(icloud)
        self.sync_trigger = PeriodicSyncFire(configs, self)
        self.sync_trigger.start()

    def start_sync_if_not_running(self) -> bool:
        if not self.sync_runner.is_alive():
            self.sync_trigger = PeriodicSyncFire(configs, self)
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
    def __init__(self, icloud:ICloud):
        super().__init__()
        self.icloud_connection = icloud

    def run(self):
        logging.warning("starting sync")
        self.icloud_connection.sync()
        logging.warning("finished sync")