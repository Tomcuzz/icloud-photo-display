""" Code to home web page """
from flask import render_template, redirect, url_for
from src.helpers.icloud import ICloud # pylint: disable=import-error
from src.helpers.sync_thread import SyncHandler # pylint: disable=import-error
from src.helpers.settings import Settings


def add_sync_status_pages(app, icloud_helper:ICloud, configs:Settings, sync_handler:SyncHandler):
    """ Add Home Page """
    @app.route("/sync-status")
    def sync_status_page():
        """ Home Page """
        if icloud_helper.is_authed and configs.icloud_album_name != "":
            return render_template('sync_status.html', ICloud_photo_album_status=icloud_helper.get_sync_photo_album_status, Sync_Running=sync_handler.sync_running())
        else:
            return redirect(url_for('settings_page'))

    @app.route("/sync-status-content/album")
    def sync_status_content_page():
        """ Home Page """
        if icloud_helper.is_authed and configs.icloud_album_name != "":
            return render_template('sync_status_content.html', ICloud_photo_album_status=icloud_helper.get_sync_photo_album_status, Sync_Running=sync_handler.sync_running())
    
    @app.route("/sync/album/<string:photoname>")
    def sync_photo_page(photoname):
        """ Sync Photo Page """
        if photoname == "all":
            sync_handler.start_album_sync_if_not_running()
            icloud_helper.sync_photo_album()
        else:
            icloud_helper.sync_photo(photname)
        return redirect(url_for('sync_status_page'))
    
    @app.route("/delete_local/<string:photname>")
    def delete_photo_page(photname):
        """ Sync Photo Page """
        icloud_helper.delete_local_photo(photname)
        return redirect(url_for('sync_status_page'))
