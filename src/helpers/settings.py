""" Module to store settings """
import json

class Settings(object):
    """ Settins storage class """
    def __init__(self, working_dir, config_file):
        self.config_file = working_dir + "/" + config_file
        self.cookie_directory = working_dir + "/cookie"
        self.photo_location = working_dir + "/photos"
        self.watch_interval = 3600
        self.loggedin = False
        self.username = ""
        self.load_settings()

    def load_settings(self):
        """ Load settings from disk """
        try:
            file = open(self.config_file, encoding="utf-8")
            data = json.load(file)
            self.photo_location = data['photo_location']
            self.cookie_directory = = data['cookie_location']
            self.watch_interval = data['watch_interval']
            self.loggedin = data['logged_in']
            self.username = data['username']
        except Exception as error:
            print('Error loading configs:', error)

    def save_settings(self):
        """ Save settings from disk """
        try:
            settings_dict = {
                'photo_location': self.photo_location,
                'cookie_location': self.cookie_directory,
                'watch_interval': self.watch_interval,
                'logged_in': self.loggedin,
                'username': self.username
            }
            settings_json = json.dumps(settings_dict)
            file = open(self.config_file,"w", encoding="utf-8")
            file.write(settings_json)
        except Exception as error:
            print('Error loading configs:', error)
