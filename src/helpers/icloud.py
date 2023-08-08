""" iCloud api connection helpers """
from src.pyicloud_ipd import utils, base, exceptions # pylint: disable=import-error
from src.helpers.settings import Settings # pylint: disable=import-error

class ICloud(object):
    """ iCloud api connection class """
    def __init__(self, configs:Settings) -> None:
        self.configs = configs
        self.api = self.setup_api()
        self.auth_passed = False
        self.auth_trusted_devices = None
        self.selected_auth_trusted_device = None

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
                    passwd
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
        self.auth_trusted_devices = self.api.trusted_devices
        trusted_devices = []
        for i, _ in enumerate(self.auth_trusted_devices):
            trusted_devices[i] = self.describe_trusted_device(i)
        return self.api.trusted_devices

    def describe_trusted_device(self, device_id:int) -> str:
        """ Get Name For Trused 2fa Devices Given ID """
        return self.auth_trusted_devices[device_id].get(
            'deviceName',
            "SMS to %s" % self.auth_trusted_devices[device_id].get('phoneNumber'))

    def send_2fa_code(self, device_id:int) -> bool:
        """ Request 2fa code send """
        if self.auth_trusted_devices is None or len(self.auth_trusted_devices) < device_id or device_id < 0:
            return False
        return self.api.send_verification_code(self.auth_trusted_devices[device_id])

    def validate_2fa_code(self, device_id:int, code:str) -> bool:
        """ Validate 2fa code """
        if self.auth_trusted_devices is None or len(self.auth_trusted_devices) < device_id or device_id < 0:
            return False
        return self.api.validate_verification_code(self.auth_trusted_devices[device_id], code)
