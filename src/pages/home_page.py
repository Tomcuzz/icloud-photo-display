""" Code to home web page """
import random
from flask import render_template
from src.helpers.app import AppHelper # pylint: disable=import-error
from src.helpers import paths # pylint: disable=import-error


def add_home_page(app, app_helper:AppHelper):
    """ Add Home Page """
    @app.route("/")
    def home_page():
        """ Home Page """
        app_helper.prom_metrics.counter__requests__photo_page.inc()
        try:
            disk_photos = paths.get_files_on_disk(app_helper.configs.photo_location)
            photo = random.choice(list(disk_photos.keys()))
            return render_template('home.html', URL=photo)
        except:
            return render_template('home.html', URL="")
