""" Code to run icloud photo display """
from flask import Flask
from src.pages import home
from src.pages import photo
from prometheus_client import Counter

app = Flask(__name__)

photo_requests_counter = Counter('photo_requests', 'Number of photo page requests')

home.add_home_page(app)
photo.add_photo_page(app, photo_requests_counter)
