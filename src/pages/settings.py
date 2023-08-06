""" Code to home web page """
from flask import render_template
from src.helpers.settings import Settings

def add_settings_pages(app, configs:Settings):
    """ Add Settings Page """
    @app.route("/settings")
    def settings_page():
        """ Settings Page """
        return render_template('settings.html', Configs=configs)

