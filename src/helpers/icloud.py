""" iCloud api connection helpers """
from src.pyicloud_ipd import utils, base, exceptions # pylint: disable=import-error
from src.helpers.settings import Settings # pylint: disable=import-error

class ICloud(object):
    """ iCloud api connection class """
    def __init__(self, configs:Settings) -> None:
        self.configs = configs
        self.api = self.setup_api()
        self.auth_passed = False

    def setup_api(self, password=None) -> base.PyiCloudService:
        """ Setup api connection """
        if not (self.configs.username != ""):
            return None

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
                if not passwd or not utils.password_exists_in_keyring(self.configs.username):
                    utils.store_password_in_keyring(self.configs.username, passwd)
                self.auth_passed = True
                return self.api
            except exceptions.NoStoredPasswordAvailable:
                self.auth_passed = False
                print('iCloud password not avalible')
            except exceptions.PyiCloudFailedLoginException:
                self.auth_passed = False
                print('iCloud Login Failed')
        return None

    def update_login(self, password):
        """ Notify that username was updated """
        self.api = self.setup_api(password)

    @property
    def is_authed(self) -> bool:
        if not self.api:
            return False
        elif not has_password:
            return False
        elif needs_2fa_setup:
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
    
    def check_photo_album_exists(self, name) -> bool:
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
            print("Photo album list error: " + err)
        return False