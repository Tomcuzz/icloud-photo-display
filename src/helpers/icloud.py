""" iCloud api connection helpers """
import os
import shutil
from datetime import datetime
from tzlocal import get_localzone # pylint: disable=import-error
from src.pyicloud_ipd import utils, base, exceptions # pylint: disable=import-error
from src.helpers.app import AppHelper # pylint: disable=import-error
from src.helpers import exif, download, paths # pylint: disable=import-error

class ICloud(): # pylint: disable=too-many-public-methods
    """ iCloud api connection class """
    def __init__(self, app:AppHelper) -> None:
        self.app = app
        self.api = self.setup_api()

    def setup_api(self, password=None) -> base.PyiCloudService:
        """ Setup api connection """
        if self.app.configs.username == "":
            return None

        passwd = None
        if password is not None:
            passwd = password.strip()

        if self.app.configs.username:
            try:
                self.app.flask_app.logger.debug(
                    'Cookie directory: ' + self.app.configs.cookie_directory)
                self.api = base.PyiCloudService(
                    domain='com',
                    apple_id=self.app.configs.username.strip(),
                    password=passwd,
                    cookie_directory=self.app.configs.cookie_directory
                )
                if passwd or not utils.password_exists_in_keyring(self.app.configs.username):
                    utils.store_password_in_keyring(self.app.configs.username, passwd)

                return self.api
            except exceptions.PyiCloudNoStoredPasswordAvailableException: #
                self.app.prom_metrics.counter__icloud__errors.inc()
                self.app.flask_app.logger.warning('iCloud password not avalible')
            except exceptions.PyiCloudFailedLoginException:
                self.app.prom_metrics.counter__icloud__errors.inc()
                self.app.flask_app.logger.exception('iCloud Login Failed')
            except exceptions.PyiCloudServiceNotActivatedErrror as e:
                self.app.prom_metrics.counter__icloud__errors.inc()
                self.app.flask_app.logger.warning('iCloud Not Activated', e)
        return None

    def update_login(self, password):
        """ Notify that username was updated """
        self.api = self.setup_api(password)

    @property
    def is_authed(self) -> bool:
        """ Check if auth'ed to icloud. """
        if not self.api:
            return False
        elif not self.has_password:
            return False
        elif self.needs_2fa_setup:
            return False
        self.run_metric_collect()
        return True

    @property
    def has_username(self) -> bool:
        """ Check if have saved username """
        return self.app.configs.username != ""

    @property
    def has_password(self) -> bool:
        """ Check if have saved password """
        return utils.password_exists_in_keyring(self.app.configs.username)

    @property
    def needs_2fa_setup(self) -> bool:
        """ Check if 2 Factor Auth Setup needed"""
        if self.api is None:
            return False
        return self.api.requires_2sa or self.api.requires_2fa

    @property
    def get_token_exparation(self) -> datetime:
        """ Return the time that the token expires. """
        exparation = None
        if not self.api:
            self.app.prom_metrics.counter__icloud__errors.inc()
            return exparation
        elif not self.has_password:
            self.app.prom_metrics.counter__icloud__errors.inc()
            return exparation
        elif self.needs_2fa_setup:
            self.app.prom_metrics.counter__icloud__errors.inc()
            return exparation
        if self.api and self.api.session and self.api.session.cookies:
            cookie_dict = {c.name: c for c in self.api.session.cookies}
            trust_key = ""
            for key in cookie_dict.keys():
                if key.startswith("X-APPLE-WEBAUTH-HSA-TRUST"):
                    trust_key = key
            if trust_key != "":
                expires = cookie_dict.get(trust_key).expires
                if expires is not None:
                    exparation = datetime.utcfromtimestamp(expires)
        return exparation

    def remove_cookies(self):
        """Remove cookie directory"""
        if self.app.configs.cookie_directory != "":
            for filename in os.listdir(self.app.configs.cookie_directory):
                file_path = os.path.join(self.app.configs.cookie_directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e: # pylint: disable=broad-exception-caught
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    def logout(self):
        """ Logout of iCloud. """
        utils.delete_password_in_keyring(self.app.configs.username)
        self.app.configs.username = ""
        self.app.configs.save_settings()
        self.remove_cookies()

    def run_metric_collect(self):
        """ Function to Collect metrics and export them. """
        token_exparation = self.get_token_exparation
        if token_exparation is not None:
            self.app.prom_metrics.gauge__icloud__token_exparation_epoch.set(
                token_exparation.timestamp())

    def get_trusted_devices(self) -> list:
        """ List Trused 2fa devices """
        trusted_devices = []
        try:
            for i in range(len(self.api.trusted_devices)):
                trusted_devices.append(self.describe_trusted_device(i))
        except exceptions.PyiCloudAPIResponseError as err:
            self.app.flask_app.logger.warning("Recieved API error:" + err.reason)
        return trusted_devices

    def describe_trusted_device(self, device_id:int) -> str:
        """ Get Name For Trused 2fa Devices Given ID """
        return self.api.trusted_devices[device_id].get(
            'deviceName',
            "SMS to %s" % self.api.trusted_devices[device_id].get('phoneNumber'))

    def send_2fa_code(self, device_id:int) -> bool:
        """ Request 2fa code send """
        if self.api.trusted_devices is None or len(
            self.api.trusted_devices) < device_id or device_id < 0:
            self.app.prom_metrics.counter__icloud__errors.inc()
            return False
        return self.api.send_verification_code(self.api.trusted_devices[device_id])

    def validate_2fa_code(self, device_id:int, code:str) -> bool:
        """ Validate 2fa code """
        if self.api.trusted_devices is None or device_id < 0:
            self.app.prom_metrics.counter__icloud__errors.inc()
            return False
        if len(self.api.trusted_devices) == device_id:
            device = {}
            return self.api.validate_2fa_code(code)
        if len(self.api.trusted_devices) > device_id:
            return self.api.validate_verification_code(self.api.trusted_devices[device_id], code)
        self.app.prom_metrics.counter__icloud__errors.inc()
        return False

    def photo_album_exists(self, name:str) -> bool:
        """ Check if a given string name is the same as an icloud alum """
        if not self.is_authed:
            self.app.prom_metrics.counter__icloud__errors.inc()
            return False
        self.setup_photo_error_handler()
        try:
            albums_dict = self.api.photos.albums
            if name in albums_dict:
                return True
        except exceptions.PyiCloudAPIResponseError as err:
            self.app.prom_metrics.counter__icloud__errors.inc()
            # For later: come up with a nicer message to the user. For now take the
            # exception text
            self.app.flask_app.logger.warning("Photo album list error: " + err)
        self.app.prom_metrics.counter__icloud__errors.inc()
        return False

    def download_photo(self, photo, download_path) -> bool:
        """ Given a path download a photo from iCloud, returns True if download is successful. """
        self.setup_photo_error_handler()
        try:
            created_date = photo.created.astimezone(get_localzone())
        except (ValueError, OSError):
            self.app.prom_metrics.counter__icloud__download_errors.inc()
            self.app.flask_app.logger.error(
                "Could not convert photo created date to local timezone (%s)",
                photo.created)
            created_date = photo.created
        download_result = download.download_media(
            self, photo, download_path, "original"
        )

        if download_result:
            self.app.prom_metrics.counter__icloud__number_of_files_downloaded.inc()
            if False and paths.clean_filename(photo.filename) \
                .lower().endswith((".jpg", ".jpeg")) and \
                not exif.get_photo_exif(download_path):
                # %Y:%m:%d looks wrong, but it's the correct format
                exif.set_photo_exif(
                    download_path,
                    created_date.strftime("%Y:%m:%d %H:%M:%S"),
                )
            download.set_utime(download_path, created_date)
        else:
            self.app.prom_metrics.counter__icloud__download_errors.inc()
        return download_result

    def setup_photo_error_handler(self):
        """Create a photo error handler"""
        if not self.is_authed:
            self.app.prom_metrics.counter__icloud__errors.inc()
            return
        def error_handler(ex, _):
            self.app.prom_metrics.counter__icloud__download_errors.inc()
            self.app.flask_app.logger.error("Photo Handler Session error")
            if "Invalid global session" in str(ex):
                if self.api:
                    self.api.authenticate()
            else:
                self.app.flask_app.logger.error("Photo Handler iCloud API error")
        try:
            self.api.photos.exception_handler = error_handler
        except exceptions.PyiCloudAPIResponseError as err:
            self.app.prom_metrics.counter__icloud__errors.inc()
            self.app.flask_app.logger.error("Photo Handler Setup error: " + err)
            error_handler(err, 0)

    @property
    def get_sync_photo_album_status(self) -> dict:
        """Get the sync phto status for the set album."""
        return self.get_album_sync_photo_album_status(
            self.app.configs.icloud_album_name,
            self.app.configs.photo_location
        )

    @property
    def get_sync_photo_all_status(self) -> dict:
        """Get the sync phto status for all photos."""
        return self.get_album_sync_photo_album_status(
            'All Photos',
            self.app.configs.all_photo_location
        )

    def get_album_sync_photo_album_status(self, album, photo_location) -> dict:
        """ Get photo sync status """
        if not self.is_authed:
            self.app.prom_metrics.counter__icloud__errors.inc()
            self.app.flask_app.logger.warning(
                "get_album_sync_photo_album_status: Icloud not logged in")
            return {}
        self.setup_photo_error_handler()
        photo_status = {}
        files_on_disk = paths.get_files_on_disk(photo_location)
        for _ in range(3): # pylint: disable=too-many-nested-blocks
            try:
                if album in self.api.photos.albums:
                    self.app.flask_app.logger.debug(
                        album + " sync - Album '" + album + "' found")
                    for photo in self.api.photos.albums[album]:
                        if photo.item_type not in ("image"):
                            continue

                        save_item = {
                            'photo': photo,
                            'local_path': paths.local_download_path_with_id(photo, photo_location),
                            'photo_dir': photo_location
                        }

                        if paths.clean_filename(photo.filename) in files_on_disk:
                            # for later: this crashes if download-size medium is specified
                            file_size = files_on_disk[paths.clean_filename(photo.filename)]['size']
                            version = photo.versions["original"]
                            photo_size = version["size"]
                            if str(file_size) != str(photo_size):
                                # Looks like files changed.... delete and recreate
                                save_item['status'] = "file-change-with-nonid-name"
                                self.app.flask_app.logger.debug(
                                    album + " sync - Photo '" + photo.filename +
                                    "' file-change-with-nonid-name with id: " + photo.id)
                            else:
                                save_item['status'] = "file-downloaded-with-nonid-name"
                                self.app.flask_app.logger.debug(
                                    album + " sync - Photo '" + photo.filename +
                                    "' file-exists-with-nonid-name with id: " + photo.id)
                        elif paths.filename_with_size_and_id(photo) in files_on_disk:
                             # for later: this crashes if download-size medium is specified
                            file_size = files_on_disk[paths.clean_filename(photo.filename)]['size']
                            version = photo.versions["original"]
                            photo_size = version["size"]
                            if str(file_size) != str(photo_size):
                                # Looks like files changed.... delete and recreate
                                save_item['status'] = "file-change"
                                self.app.flask_app.logger.debug(
                                    album + " sync - Photo '" + photo.filename +
                                    "' file-change with id: " + photo.id)
                            else:
                                save_item['status'] = "file-downloaded"
                                self.app.flask_app.logger.debug(
                                    album + " sync - Photo '" + photo.filename +
                                    "' file-exists with id: " + photo.id)
                        else:
                            save_item['status'] = "non-existent"
                            self.app.flask_app.logger.debug(
                                album + " sync - Photo '" + photo.filename +
                                "' file-does-not-exist")

                        if photo.filename in photo_status:
                            photo_status[photo.filename]['status'] = "file-name-duplicated"
                            self.app.flask_app.logger.debug(
                                album + " sync - Photo '" + photo.filename +
                                "' file-name-duplicated" + " with id: " + photo.id)
                        else:
                            photo_status[photo.filename] = save_item
                else:
                    self.app.flask_app.logger("Photo Album '" + album + "' not found")
                # Break as we now got to end of sync and dont need to retry
                break
            except exceptions.PyiCloudAPIResponseError as err:
                self.app.prom_metrics.counter__icloud__errors.inc()
                if "Invalid global session" in str(err):
                    self.app.flask_app.logger.error("Photo List Get Session error")
                    if self.api:
                        self.api.authenticate()
                else:
                    self.app.flask_app.logger.error("iCloud API error: " + err)

        file_synced = 0
        file_change_num = 0
        file_synced_with_nonid_name = 0
        file_change_num_with_nonid_name = 0
        file_does_not_exist_num = 0
        file_name_duplicated_num = 0
        file_unkown_state = 0
        for _, status in photo_status.items():
            if status['status'] == "file-downloaded":
                file_synced += 1
            elif status['status'] == "file-change":
                file_change_num += 1
            if status['status'] == "file-downloaded-with-nonid-name":
                file_synced_with_nonid_name += 1
            elif status['status'] == "file-change-with-nonid-name":
                file_change_num_with_nonid_name += 1
            elif status['status'] == "non-existent":
                file_does_not_exist_num += 1
            elif status['status'] == "file-name-duplicated":
                file_name_duplicated_num += 1
            else:
                file_unkown_state += 1
        self.app.prom_metrics.gauge__icloud__photo_sync_state.labels(
                SyncName=album, status="file_synced").set(file_synced)
        self.app.prom_metrics.gauge__icloud__photo_sync_state.labels(
                SyncName=album, status="file_change").set(file_change_num)
        self.app.prom_metrics.gauge__icloud__photo_sync_state.labels(
                SyncName=album, status="file_synced_with_nonid_name").set(
                    file_synced_with_nonid_name)
        self.app.prom_metrics.gauge__icloud__photo_sync_state.labels(
                SyncName=album, status="file_change_with_nonid_name").set(
                    file_change_num_with_nonid_name)
        self.app.prom_metrics.gauge__icloud__photo_sync_state.labels(
                SyncName=album, status="not_existent").set(file_does_not_exist_num)
        self.app.prom_metrics.gauge__icloud__photo_sync_state.labels(
                SyncName=album, status="file_name_duplicated").set(file_name_duplicated_num)
        self.app.prom_metrics.gauge__icloud__photo_sync_state.labels(
                SyncName=album, status="unkown").set(file_unkown_state)

        return photo_status

    def delete_local_photo(self, name, photos=None) -> bool:
        """ Delete a local photo """
        result = False
        photos = self.get_sync_photo_album_status
        if name in photos:
            download_path = paths.local_download_path(
                photos[name]['photo'],
                photo[name]['photo_dir'])
            if os.path.exists(download_path):
                os.remove(download_path)
                result = True
            id_path = paths.local_download_path_with_id(
                photos[name]['photo'],
                photo[name]['photo_dir']
                self.app.configs.photo_location)
            if os.path.exists(id_path):
                os.remove(id_path)
                result = True
        return result
    
    def update_local_file_to_id(self, photo:dict) -> bool:
        old_path = paths.local_download_path(
            photos['photo'],
            photo['photo_dir'])
        new_path = paths.local_download_path_with_id(
            photos['photo'],
            photo['photo_dir'])
        if os.path.exists(old_path) and not os.path.exists(new_path):
            self.app.flask_app.logger.debug("Moving Photo from: " + old_path + " to: " + new_path)
            os.rename(old_path, new_path)
            return True
        return False

    def sync_photo(self, name, photos=None) -> bool:
        """ Download photo to local path, returns True if no errors. """
        self.setup_photo_error_handler()
        if photos is None:
            photos = self.get_sync_photo_album_status
        if name in photos:
            if photos[name]['status'] == "non-existent":
                self.app.flask_app.logger.debug("Downloading photo: " + name)
                return self.download_photo(photos[name]['photo'], photos[name]['local_path'])
            elif photos[name]['status'] == "file-name-duplicated":
                self.app.flask_app.logger.debug("Deleting photo: " + name)
                return self.delete_local_photo(name, photos)
                self.app.flask_app.logger.debug("Photo: " + name + " deleted (will by downloaded on next run)")
            elif photos[name]['status'] == "file-change-with-nonid-name":
                self.app.flask_app.logger.debug("Moving Photo photo: " + name)
                return self.update_local_file_to_id(photos[name])
            # Delete File names that are duplicated to clean up duplication bug
            # elif photos[name]['status'] == "file-name-duplicated":
            #     self.app.flask_app.logger.debug("Deleting photo: " + name)
            #     return self.delete_local_photo(name, photos)
            # Disabling till multiple photos with same name issue fixed
            # elif photos[name]['status'] == "file-change":
            #     self.app.flask_app.logger.debug("Deleting photo: " + name)
            #     return self.delete_local_photo(name, photos)
            #     self.app.flask_app.logger.debug("Downloading photo: " + name)
            #     return self.download_photo(photos[name]['photo'], photos[name]['local_path'])
        return True


    def sync_album(self, sync_all_photos=False):
        """ Download missing photos to local path """
        if self.is_authed:
            album_name = 'All Photos'
            download_path = self.app.configs.all_photo_location
            if not sync_all_photos:
                album_name = self.app.configs.icloud_album_name
                download_path = self.app.configs.photo_location
            self.app.prom_metrics.enum__icloud__sync_running_status.labels(
                SyncName=album_name).state('running')
            start = datetime.now()
            self.setup_photo_error_handler()
            self.app.flask_app.logger.debug(album_name + " Sync - Getting statuses")
            photos = self.get_album_sync_photo_album_status(album_name, download_path)
            self.app.flask_app.logger.debug(album_name + " Sync - Photo Status Recieved")
            download_failures = 0
            for photo in photos:
                self.app.flask_app.logger.debug("Syncing photo: " + photo)
                if not self.sync_photo(photo, photos):
                    download_failures += 1
                if download_failures > self.app.configs.max_download_attempts:
                    self.app.prom_metrics.gauge__icloud__sync_errors.labels(
                        SyncName=album_name).inc()
                    self.app.flask_app.logger.warning("Reached max download attempts")
                    self.app.prom_metrics.enum__icloud__sync_running_status.labels(
                        SyncName=album_name).state('waiting')
                    self.app.prom_metrics.gauge__icloud__sync_errors.labels(
                        SyncName=album_name).set(0)
                    return
            end = datetime.now()
            self.app.prom_metrics.gauge__icloud__last_sync_elapse_time.labels(
                SyncName=album_name).set((end - start).total_seconds())
            self.app.prom_metrics.gauge__icloud__last_sync_epoch.labels(
                SyncName=album_name).set(end.timestamp())
            self.app.prom_metrics.enum__icloud__sync_running_status.labels(
                SyncName=album_name).state('waiting')
            self.app.prom_metrics.gauge__icloud__sync_errors.labels(
                SyncName=album_name).set(0)
            self.run_metric_collect()
        else:
            self.app.flask_app.logger.warning("Tried to sync when not authed to iCloud")
