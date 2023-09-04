""" Code to run icloud photo display """
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from src.pages import home_page
from src.pages import photo_page
from src.pages import sync_status
from src.pages import settings_page
from src.helpers.app import AppHelper

app = Flask(__name__)

app_helper = AppHelper()

home_page.add_home_page(app, app_helper.prom_metrics, app_helper.configs)
photo_page.add_photo_page(app, app_helper.prom_metrics, app_helper.configs)
sync_status.add_sync_status_pages(app, app_helper.icloud_helper, app_helper.configs, app_helper.sync_handler)
settings_page.add_settings_pages(app, app_helper.prom_metrics, app_helper.configs, app_helper.icloud_helper)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})