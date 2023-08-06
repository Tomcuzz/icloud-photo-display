""" Code to home web page """
from flask import render_template
from src.helpers import settings

def add_settings_pages(app, configs:settings.Settings):
    """ Add Settings Page """
    @app.route("/settings")
    def settings_page():
        """ Settings Page """
        return render_template('settings.html', Configs=configs)

