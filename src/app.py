""" Code to run icloud photo display """
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home_page():
    """ Home Page """
    return "<p>Hello, World!</p>"
