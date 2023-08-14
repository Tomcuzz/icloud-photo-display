""" Code to photo web page """
import os
import random
import logging
from flask import render_template, abort, send_file
from src.helpers.settings import Settings # pylint: disable=import-error
from src.helpers.metrics import Metrics # pylint: disable=import-error
from src.helpers import paths # pylint: disable=import-error
from wand.image import Image

def add_photo_page(app, app_metrics:Metrics, configs:Settings):
    """ Add Home Page """
    @app.route("/photo")
    @app.route('/photo/<int:refresh>')
    def photo_page(refresh=900):
        """ Photo Page """
        app_metrics.photo_requests_counter.inc()
        disk_photos = paths.get_files_on_disk(configs.photo_location)
        photo = random.choice(list(disk_photos.keys()))
        return render_template('photo.html', URL=photo)

    @app.route('/photo/<string:filename>')
    def photo_contents(filename=""):
        if filename == "":
            abort(404)
        disk_photos = paths.get_files_on_disk(configs.photo_location)
        logging.warning(disk_photos[filename]['file_path'])
        if  filename not in disk_photos:
            abort(404)
        if not os.path.isfile(disk_photos[filename]['file_path']):
            abort(404)
        filecontent = open(disk_photos[filename]['file_path'], "rb")
        # return filecontent.read()
        return send_file(filecontent, download_name=filename)
        # with Image(filename=filepath) as img:
        #     return send_file(img.make_blob('jpeg'))
