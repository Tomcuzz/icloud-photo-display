""" Code to run icloud photo display """
from flask import Flask
from prometheus_client import Counter
from src.pages import home
from src.pages import photo
from src.helpers import settings, metrics

app = Flask(__name__)
configs = settings.Settings("/icloudpd", "configs.json")
prom_metrics = metrics.Metrics()

home.add_home_page(app)
photo.add_photo_page(app, prom_metrics, configs)
