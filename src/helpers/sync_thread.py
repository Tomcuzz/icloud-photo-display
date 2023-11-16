import logging
from time import sleep
from datetime import datetime
from threading import Thread, Lock
from src.helpers.app import AppHelper # pylint: disable=import-error
from src.helpers.icloud import ICloud # pylint: disable=import-error
from src.helpers.settings import Settings # pylint: disable=import-error

class SyncHandler(object):
    def __init__(self, app:AppHelper):
        self.app = app
        self.sync_runner = SyncThread(self.app)
        self.sync_trigger = AlbumPeriodicSyncFire(self.app, self)
        self.sync_trigger.start()

    def start_album_sync_if_not_running(self) -> bool:
        if not self.sync_runner.is_alive():
            self.sync_runner = SyncThread(self.app)
            self.sync_runner.album_waiting = True
            self.sync_runner.start()
            return True
        else:
            self.sync_runner.album_waiting = True
            return False

    def start_all_sync_if_not_running(self) -> bool:
        if not self.sync_runner.is_alive():
            self.sync_runner = SyncThread(self.app)
            self.sync_runner.all_waiting = True
            self.sync_runner.start()
            return True
        else:
            self.sync_runner.all_waiting = True
            return False
    
    def sync_running(self) -> bool:
        return self.sync_runner.is_alive()

class AlbumPeriodicSyncFire(Thread):
    def __init__(self, app:AppHelper, sync_handler:SyncHandler):
        super().__init__()
        self.app = app
        self.sync_handler = sync_handler
    
    def run(self):
        while True:
            if int(self.app.configs.watch_interval) > 0:
                self.sync_handler.start_album_sync_if_not_running()
                self.app.prom_metrics.gauge__icloud__next_sync_epoch.labels(SyncName=self.app.configs.icloud_album_name).set((datetime.now().timestamp() + self.app.configs.watch_interval))
                sleep(int(self.app.configs.watch_interval))

class AllPeriodicSyncFire(Thread):
    def __init__(self, app:AppHelper, sync_handler:SyncHandler):
        super().__init__()
        self.app = app
        self.sync_handler = sync_handler
    
    def run(self):
        while True:
            if int(self.app.configs.all_watch_interval) > 0:
                self.sync_handler.start_all_sync_if_not_running()
                self.app.prom_metrics.gauge__icloud__next_sync_epoch.labels(SyncName='All Photos').set((datetime.now().timestamp() + self.app.configs.all_watch_interval))
                sleep(int(self.app.configs.all_watch_interval))


class SyncThread(Thread):
    def __init__(self, app:AppHelper):
        super().__init__()
        self.app = app
        self.all_waiting = False
        self.album_waiting = False

    def run(self):
        while self.all_waiting and self.album_waiting:
            if self.all_waiting:
                logging.warning("starting all sync")
                self.all_waiting = False
                self.app.icloud_helper.sync_all()
                logging.warning("finished all sync")
            if self.album_waiting:
                logging.warning("starting album sync")
                self.album_waiting = False
                self.app.icloud_helper.sync_album()
                logging.warning("finished album sync")
