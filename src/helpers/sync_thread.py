from time import sleep
from threading import Thread
from src.helpers.icloud import ICloud # pylint: disable=import-error
from src.helpers.settings import Settings # pylint: disable=import-error

class SyncThreadHandler(object):
    def __init__(self, configs:Settings, icloud:ICloud):
        self.sync_runner = SyncThread()
        self.sync_trigger = PeriodicSyncFire(configs, self)
        self.sync_trigger.start()

    def start_sync(self):
        if not self.sync_runner.sync_lock.locked():
            self.sync_runner.run()

class PeriodicSyncFire(Thread):
    def __init__(self, configs:Settings, sync_handler:SyncThreadHandler):
        super().__init__()
        self.configs = configs
        self.sync_handler = sync_handler
    
    def run(self):
        while True:
            if self.configs.watch_interval > 0:
                self.sync_handler.start_sync()
                sleep(self.configs.watch_interval)


class SyncThread(Thread):
    def __init__(self, icloud:ICloud):
        super().__init__()
        self.sync_lock = threading.Lock()
        self.icloud_connection = icloud

    def run(self):
        with self.sync_lock:
            self.icloud_connection.sync()