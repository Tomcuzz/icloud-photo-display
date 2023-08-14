""" Code to photo web page """
import os
import random
from flask import render_template, abort, send_file
from src.helpers.settings import Settings # pylint: disable=import-error
from src.helpers.metrics import Metrics # pylint: disable=import-error
from wand.image import Image

def add_photo_page(app, app_metrics:Metrics, configs:Settings):
    """ Add Home Page """
    @app.route("/photo")
    @app.route('/photo/<int:refresh>')
    def photo_page(refresh=900):
        """ Photo Page """
        app_metrics.photo_requests_counter.inc()
        photo = random.choice(os.listdir(configs.photo_location))
        return render_template('photo.html', Refresh=refresh, URL=photo)

    @app.route('/photo/<string:filename>')
    def photo_contents(filename=""):
        filepath = configs.photo_location + "/" + filename
        if filename == "" or len(filename.split()) > 1 or not os.path.isfile(filepath):
            abort(404)
        filecontent = open(filepath, "rb")
        # return filecontent.read()
        return send_file(filecontent, download_name=filename)
        # with Image(filename=filepath) as img:
        #     return send_file(img.make_blob('jpeg'))
