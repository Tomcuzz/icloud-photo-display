""" Code to home web page """
from flask import render_template


def add_home_page(app):
    """ Add Home Page """
    @app.route("/")
    def home_page():
        """ Home Page """
        return render_template('home.html')
