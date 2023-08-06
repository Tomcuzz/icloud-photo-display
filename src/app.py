""" Code to run icloud photo display """
from flask import Flask
from src.pages import home
from src.pages import photo
from src.helpers.settings import Settings
from src.helpers.metrics import Metrics

app = Flask(__name__)
configs = Settings("/icloudpd", "configs.json")
prom_metrics = Metrics()

home.add_home_page(app)
photo.add_photo_page(app, prom_metrics, configs)
