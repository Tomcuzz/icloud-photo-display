""" Code to home web page """
from flask import render_template, request, redirect, url_for
from src.helpers.settings import Settings

def add_settings_pages(app, configs:Settings):
    """ Add Settings Page """
    @app.route("/settings", methods=['GET', 'POST'])
    def settings_page():
        """ Settings Page """
        if (request.method == 'POST' and
            request.form['photo_location'] != "" and
            request.form['user'] != "" and
            request.form['pass'] != ""):
            configs.photo_location = request.form['photo_location']
            configs.username = request.form['user']
            configs.password = request.form['pass']
            configs.save_settings()
            return redirect(url_for('home_page'))

        return render_template('settings.html', Configs=configs)
