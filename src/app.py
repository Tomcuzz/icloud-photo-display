""" Code to run icloud photo display """
from flask import Flask
from src.pages import home_page
from src.pages import photo_page
from src.pages import settings_page
from src.helpers.settings import Settings
from src.helpers.metrics import Metrics
from src.helpers.icloud import ICloud

app = Flask(__name__)
configs = Settings("/icloudpd", "configs.json")
prom_metrics = Metrics()
icloud_helper = ICloud(configs)

home_page.add_home_page(app)
photo_page.add_photo_page(app, prom_metrics, configs)
settings_page.add_settings_pages(app, configs, icloud_helper)
