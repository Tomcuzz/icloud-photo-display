""" Code to photo web page """
import os
import io
import random
from flask import render_template, abort, send_file, request
from wand.image import Image
from wand.resource import limits
from src.helpers.app import AppHelper # pylint: disable=import-error
from src.helpers import paths # pylint: disable=import-error

def add_photo_page(app, app_helper:AppHelper):
    """ Add Home Page """
    @app.route("/photo")
    @app.route('/photo/<int:refresh>')
    def photo_page(refresh=900):
        """ Photo Page """
        app_helper.prom_metrics.counter__requests__photo_page.inc()
        try:
            disk_photos = paths.get_files_on_disk(app_helper.configs.photo_location)
            photo = random.choice(list(disk_photos.keys()))
            return render_template('photo.html', URL=photo)
        except:
            return render_template('home.html', URL="")

    @app.route('/photo/<string:filename>')
    def photo_contents(filename=""):
        if filename == "":
            app_helper.prom_metrics.counter__error__404.inc()
            abort(404)
        disk_photos = paths.get_files_on_disk(app_helper.configs.photo_location)
        if filename == "random": # If we set random as string get one randomly from disk
            filename = random.choice(list(disk_photos.keys()))
            app_helper.flask_app.logger.info("Random Image providing: " + filename)
        if  filename not in disk_photos:
            app_helper.prom_metrics.counter__error__404.inc()
            abort(404)
        if not os.path.isfile(disk_photos[filename]['file_path']):
            app_helper.prom_metrics.counter__error__404.inc()
            abort(404)

        width = request.args.get('width', default = -1, type = int)
        height = request.args.get('height', default = -1, type = int)

            
        # Use 1GB of ram before writing temp data to disk.
        limits['memory'] = 1024 * 1024 * 1024
        # Reject images larger than 100000x100000.
        limits['width'] = 1000000
        limits['height'] = 1000000
        with Image(filename=disk_photos[filename]['file_path']) as img:
            if width > 0 and height > 0:
                img.transform(resize=f"{width}x{height}>")
            return send_file(
                io.BytesIO(img.make_blob('jpeg')),
                mimetype='image/jpeg',
                as_attachment=False,
                download_name='%s.jpg' % disk_photos[filename]['file_name'])
