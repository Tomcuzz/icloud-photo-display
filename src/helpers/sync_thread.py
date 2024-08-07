from time import sleep
from datetime import datetime
from threading import Thread
from src.helpers.app import AppHelper # pylint: disable=import-error

class SyncHandler(object):
    def __init__(self, app:AppHelper):
        self.app = app
        self.sync_runner = SyncThread(self.app)
        if int(self.app.configs.all_watch_interval) > 0:
            self.sync_runner.all_waiting = True
        if int(self.app.configs.watch_interval) > 0:
            self.sync_runner.album_waiting = True
        self.album_sync_trigger = AlbumPeriodicSyncFire(self.app, self)
        self.album_sync_trigger.start()
        self.all_sync_trigger = AllPeriodicSyncFire(self.app, self)
        self.all_sync_trigger.start()

    def start_album_sync_if_not_running(self) -> bool:
        if not self.sync_runner.is_alive():
            self.app.flask_app.logger.info("Starting new sync thread for album")
            self.sync_runner = SyncThread(self.app)
            self.sync_runner.album_waiting = True
            self.sync_runner.start()
            return True
        self.app.flask_app.logger.info("Using existing sync thread for album")
        self.sync_runner.album_waiting = True
        return False

    def start_all_sync_if_not_running(self) -> bool:
        if not self.sync_runner.is_alive():
            self.app.flask_app.logger.info("Starting new sync thread for all")
            self.sync_runner = SyncThread(self.app)
            self.sync_runner.all_waiting = True
            self.sync_runner.start()
            return True
        self.app.flask_app.logger.info("Using existing sync thread for all")
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
                self.app.prom_metrics.gauge__icloud__next_sync_epoch.labels(
                    SyncName=self.app.configs.icloud_album_name
                    ).set((datetime.now().timestamp() + self.app.configs.watch_interval))
                sleep(int(self.app.configs.watch_interval))
            else:
                sleep(1800)

class AllPeriodicSyncFire(Thread):
    def __init__(self, app:AppHelper, sync_handler:SyncHandler):
        super().__init__()
        self.app = app
        self.sync_handler = sync_handler

    def run(self):
        while True:
            if int(self.app.configs.all_watch_interval) > 0:
                self.sync_handler.start_all_sync_if_not_running()
                self.app.prom_metrics.gauge__icloud__next_sync_epoch.labels(
                    SyncName='All Photos'
                    ).set((datetime.now().timestamp() + self.app.configs.all_watch_interval))
                sleep(int(self.app.configs.all_watch_interval))
            else:
                sleep(1800)


class SyncThread(Thread):
    def __init__(self, app:AppHelper):
        super().__init__()
        self.app = app
        self.all_waiting = False
        self.album_waiting = False

    def run(self):
        while self.all_waiting or self.album_waiting:
            if self.all_waiting:
                self.app.flask_app.logger.info("starting all sync")
                self.all_waiting = False
                self.app.icloud_helper.sync_album(sync_all_photos=True)
                self.app.flask_app.logger.info("finished all sync")
            if self.album_waiting:
                self.app.flask_app.logger.info("starting album sync")
                self.album_waiting = False
                self.app.icloud_helper.sync_album()
                self.app.flask_app.logger.info("finished album sync")
