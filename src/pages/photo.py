""" Code to home web page """
import os
from flask import abort

def add_photo_page(app):
    """ Add Home Page """
    @app.route("/photo")
    @app.route('/photo/<int:refresh>')
    def photo_page(refresh=900):
        """ Photo Page """
        return "<p>Photo page to go here! <br> Refresh is: " + str(refresh) + "</p>"

    @app.route('/photo/<string:filename>')
    def photo_contents(filename=""):
        filepath = "/photos/"+filename
        if filename == "" or len(filename.split()) > 1 or not os.path.isfile(filepath):
            abort(404)
        filecontent = open(filepath, "r", encoding="utf-8")
        return filecontent.read()
