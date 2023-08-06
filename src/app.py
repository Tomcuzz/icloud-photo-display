""" Code to run icloud photo display """
from flask import Flask
from src.pages import home

app = Flask(__name__)

home.add_home_page(app)
