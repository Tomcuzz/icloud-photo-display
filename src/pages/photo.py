""" Code to home web page """
import os
import random
from flask import render_template, abort
from prometheus_client import Counter
from src.helpers import settings

def add_photo_page(app, photo_requests_counter:Counter, configs:settings.Settings):
    """ Add Home Page """
    @app.route("/photo")
    @app.route('/photo/<int:refresh>')
    def photo_page(refresh=900):
        """ Photo Page """
        photo_requests_counter.inc()
        photo = random.choice(os.listdir(configs.photo_location))
        return render_template('photo.html', Refresh=refresh, URL=photo)

    @app.route('/photo/<string:filename>')
    def photo_contents(filename=""):
        filepath = configs.photo_location + "/" + filename
        if filename == "" or len(filename.split()) > 1 or not os.path.isfile(filepath):
            abort(404)
        filecontent = open(filepath, "r", encoding="utf-8")
        return filecontent.read()
