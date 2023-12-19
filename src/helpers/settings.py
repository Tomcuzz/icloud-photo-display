""" Module to store settings """
import json

class Settings(): # pylint: disable=too-many-instance-attributes
    """ Settins storage class """
    def __init__(self, working_dir, config_file):
        self.config_file = working_dir + "/" + config_file
        self.cookie_directory = working_dir + "/cookie"
        self.photo_location = working_dir + "/photos"
        self.all_photo_location = working_dir + "/all-photos"
        self.photo_state_cache_path = working_dir + "/photo_state_cache.json"
        self.photo_state_cache_lifetime = 3600 # In Seconds (1 Hour)
        self.icloud_album_name = ""
        self.watch_interval = 3600
        self.all_watch_interval = 0
        self.loggedin = False
        self.username = ""
        self.max_retries = 5
        self.wait_seconds = 10
        self.max_download_attempts = 20
        self.load_settings()

    def load_settings(self):
        """ Load settings from disk """
        try:
            file = open(self.config_file, encoding="utf-8")
            data = json.load(file)
            if 'all_photo_location' in data:
                self.all_photo_location = data['all_photo_location']
            if 'photo_location' in data:
                self.photo_location = data['photo_location']
            if 'cookie_directory' in data:
                self.cookie_directory = data['cookie_directory']
            if 'all_watch_interval' in data:
                self.all_watch_interval = data['all_watch_interval']
            if 'watch_interval' in data:
                self.watch_interval = data['watch_interval']
            if 'icloud_album_name' in data:
                self.icloud_album_name = data['icloud_album_name']
            if 'logged_in' in data:
                self.loggedin = data['logged_in']
            if 'username' in data:
                self.username = data['username']
        except Exception as error: # pylint: disable=broad-exception-caught
            print('Error loading configs:', error)

    def save_settings(self):
        """ Save settings from disk """
        try:
            settings_dict = {
                'all_photo_location': self.all_photo_location,
                'photo_location': self.photo_location,
                'cookie_directory': self.cookie_directory,
                'all_watch_interval': self.all_watch_interval,
                'watch_interval': self.watch_interval,
                'icloud_album_name': self.icloud_album_name,
                'logged_in': self.loggedin,
                'username': self.username
            }
            settings_json = json.dumps(settings_dict)
            file = open(self.config_file,"w", encoding="utf-8")
            file.write(settings_json)
        except Exception as error: # pylint: disable=broad-exception-caught
            print('Error loading configs:', error)
