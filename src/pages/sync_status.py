""" Code to home web page """
from flask import render_template, redirect, url_for
from src.helpers.icloud import ICloud # pylint: disable=import-error


def add_sync_status_pages(app, icloud_helper:ICloud):
    """ Add Home Page """
    @app.route("/sync-status")
    def sync_status_page():
        """ Home Page """
        if icloud_helper.is_authed:
            return render_template('sync_status.html', ICloud=icloud_helper)
        else:
            return redirect(url_for('settings_page'))
    
    @app.route("/sync/<string:photname>")
    def sync_photo_page(photname):
        """ Sync Photo Page """
        if photname == "all":
            icloud_helper.sync_photo_album()
        else:
            icloud_helper.sync_photo(photname)
        return redirect(url_for('sync_status_page'))
