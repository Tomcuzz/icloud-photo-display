""" Code to run icloud photo display """
from flask import Flask
from src.pages import home
from src.pages import photo

app = Flask(__name__)



home.add_home_page(app)
photo.add_photo_page(app)
