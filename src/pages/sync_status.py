""" Code to home web page """
from flask import render_template, redirect, url_for
from src.helpers.app import AppHelper # pylint: disable=import-error


def add_sync_status_pages(app, app_helper:AppHelper):
    """ Add Home Page """
    @app.route("/sync-status")
    def sync_status_page():
        """ Home Page """
        if app_helper.icloud_helper.is_authed and app_helper.configs.icloud_album_name != "":
            return render_template(
                'sync_status.html',
                ICloud_photo_album_status=app_helper.icloud_helper.get_sync_photo_album_status,
                Sync_Running=app_helper.sync_handler.sync_running())
        else:
            return redirect(url_for('settings_page'))

    @app.route("/sync-status-content/album")
    def sync_status_content_page():
        """ Home Page """
        if app_helper.icloud_helper.is_authed and app_helper.configs.icloud_album_name != "":
            return render_template(
                'sync_status_content.html',
                ICloud_photo_album_status=app_helper.icloud_helper.get_sync_photo_album_status,
                Sync_Running=app_helper.sync_handler.sync_running())

    @app.route("/sync/album/<string:photoname>")
    def sync_photo_page(photoname):
        """ Sync Photo Page """
        if photoname == "all":
            app_helper.sync_handler.start_album_sync_if_not_running()
            app_helper.icloud_helper.sync_album()
        else:
            app_helper.icloud_helper.sync_photo(photoname)
        return redirect(url_for('sync_status_page'))

    @app.route("/delete_local/<string:photname>")
    def delete_photo_page(photname):
        """ Sync Photo Page """
        photos = self.get_sync_photo_album_status
        if photname in photos:
            app_helper.icloud_helper.delete_local_photo(photos[photname])
        return redirect(url_for('sync_status_page'))
