""" Code to run icloud photo display """
from flask import Flask
from prometheus_client import Counter
from src.pages import home
from src.pages import photo
from src.helpers import settings

app = Flask(__name__)
configs = settings.Settings("/icloudpd", "configs.json")

photo_requests_counter = Counter('photo_requests', 'Number of photo page requests')

home.add_home_page(app)
photo.add_photo_page(app, photo_requests_counter, configs)
