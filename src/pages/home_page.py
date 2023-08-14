""" Code to home web page """
import os
import random
from flask import render_template
from src.helpers.settings import Settings # pylint: disable=import-error
from src.helpers.metrics import Metrics # pylint: disable=import-error
from src.helpers import paths # pylint: disable=import-error


def add_home_page(app, app_metrics:Metrics, configs:Settings):
    """ Add Home Page """
    @app.route("/")
    def home_page():
        """ Home Page """
        app_metrics.photo_requests_counter.inc()
        disk_photos = paths.get_files_on_disk(configs.photo_location)
        photo = random.choice(list(disk_photos.keys()))
        return render_template('home.html', URL=photo)
