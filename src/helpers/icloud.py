""" iCloud api connection helpers """
from src.pyicloud_ipd import utils, base, exceptions # pylint: disable=import-error
from src.helpers.settings import Settings # pylint: disable=import-error
from src.helpers import exif, download, paths # pylint: disable=import-error
import piexif
import logging
from piexif._exceptions import InvalidImageDataError
from tzlocal import get_localzone

class ICloud(object):
    """ iCloud api connection class """
    def __init__(self, configs:Settings) -> None:
        self.configs = configs
        self.api = self.setup_api()

    def setup_api(self, password=None) -> base.PyiCloudService:
        """ Setup api connection """
        if not (self.configs.username != ""):
            return None

        passwd = None
        if password != None:
            passwd = password.strip()

        if self.configs.username:
            try:
                self.api = base.PyiCloudService(
                    "com",
                    self.configs.username.strip(),
                    passwd,
                    cookie_directory=self.configs.cookie_directory
                )
                if passwd or not utils.password_exists_in_keyring(self.configs.username):
                    utils.store_password_in_keyring(self.configs.username, passwd)
                return self.api
            except exceptions.NoStoredPasswordAvailable:
                logging.warning('iCloud password not avalible')
            except exceptions.PyiCloudFailedLoginException:
                logging.warning('iCloud Login Failed')
        return None

    def update_login(self, password):
        """ Notify that username was updated """
        self.api = self.setup_api(password)

    @property
    def is_authed(self) -> bool:
        if not self.api:
            return False
        elif not self.has_password:
            return False
        elif self.needs_2fa_setup:
            return False
        return True

    @property
    def has_username(self) -> bool:
        """ Check if have saved username """
        return self.configs.username != ""

    @property
    def has_password(self) -> bool:
        """ Check if have saved password """
        return utils.password_exists_in_keyring(self.configs.username)

    @property
    def needs_2fa_setup(self) -> bool:
        """ Check if 2 Factor Auth Setup needed"""
        if self.api is None:
            return False
        return self.api.requires_2sa

    def get_trusted_devices(self) -> list:
        """ List Trused 2fa devices """
        trusted_devices = []
        for i in range(len(self.api.trusted_devices)):
            trusted_devices.append(self.describe_trusted_device(i))
        return trusted_devices

    def describe_trusted_device(self, device_id:int) -> str:
        """ Get Name For Trused 2fa Devices Given ID """
        return self.api.trusted_devices[device_id].get(
            'deviceName',
            "SMS to %s" % self.api.trusted_devices[device_id].get('phoneNumber'))

    def send_2fa_code(self, device_id:int) -> bool:
        """ Request 2fa code send """
        if self.api.trusted_devices is None or len(self.api.trusted_devices) < device_id or device_id < 0:
            return False
        return self.api.send_verification_code(self.api.trusted_devices[device_id])

    def validate_2fa_code(self, device_id:int, code:str) -> bool:
        """ Validate 2fa code """
        if self.api.trusted_devices is None or device_id < 0:
            return False
        if len(self.api.trusted_devices) == device_id:
            device = {}
            return self.api.validate_verification_code(device, code)
        if len(self.api.trusted_devices) > device_id:
            return self.api.validate_verification_code(self.api.trusted_devices[device_id], code)
        return False
    
    def photo_album_exists(self, name:str) -> bool:
        """ Check if a given string name is the same as an icloud alum """
        if not self.is_authed:
            return False
        try:
            albums_dict = self.api.photos.albums
            if name in albums_dict:
                return True
        except PyiCloudAPIResponseError as err:
            # For later: come up with a nicer message to the user. For now take the
            # exception text
            logging.warning("Photo album list error: " + err)
        return False
    
    def download_photo(self, photo, path) -> bool:
        """ Given a path download a photo from iCloud """
        try:
            created_date = photo.created.astimezone(get_localzone())
        except (ValueError, OSError):
            logging.error(
                "Could not convert photo created date to local timezone (%s)",
                photo.created)
            created_date = photo.created
        download_result = download.download_media(
            self, photo, download_path, "original"
        )
        
        if download_result:
            if set_exif_datetime and \
                paths.clean_filename(photo.filename) \
                .lower().endswith((".jpg", ".jpeg")) and \
                not exif.get_photo_exif(download_path):
                    # %Y:%m:%d looks wrong, but it's the correct format
                    date_str = created_date.strftime(
                        "%Y-%m-%d %H:%M:%S%z")
                    set_photo_exif(
                        download_path,
                        created_date.strftime("%Y:%m:%d %H:%M:%S"),
                    )
            download.set_utime(download_path, created_date)
    
    @property
    def get_sync_photo_album_status(self):
        """ Get photo sync status """
        photo_status = {}
        for photo in self.api.photos.albums[self.configs.icloud_album_name]:
            if photo.item_type not in ("image"):
                continue
            
            download_path = paths.local_download_path(photo, "original", self.configs.photo_location)

            save_item = {
                'photo': photo,
                'local_path': download_path
            }

            file_exists = os.path.isfile(download_path)
            if file_exists:
                # for later: this crashes if download-size medium is specified
                file_size = os.stat(download_path).st_size
                version = photo.versions["original"]
                photo_size = version["size"]
                if file_size != photo_size:
                    # Looks like files changed.... delete and recreate
                    save_item['status'] = "file-change"
                else:
                    save_item['status'] = "file-downloaded"

            if not file_exists:
                save_item['status'] = "non-existent"
            
            photo_status[photo.filename] = save_item
        return photo_status

    def sync_photo_album(self):
        """ Download missing photos to local path """
        for photo in self.api.photos.albums[self.configs.icloud_album_name]:
            if photo.item_type not in ("image"):
                continue
            
            download_path = paths.local_download_path(photo, "original", self.configs.photo_location)
            file_exists = os.path.isfile(download_path)
            if file_exists:
                # for later: this crashes if download-size medium is specified
                file_size = os.stat(download_path).st_size
                version = photo.versions["original"]
                photo_size = version["size"]
                if file_size != photo_size:
                    # Looks like files changed.... delete and recreate
                    continue

            if not file_exists:
                self.download_photo(photo, download_path)
