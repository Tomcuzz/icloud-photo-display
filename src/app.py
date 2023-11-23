""" Code to run icloud photo display """
import os
import logging
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from src.pages import home_page
from src.pages import photo_page
from src.pages import sync_status
from src.pages import settings_page
from src.helpers.app import AppHelper

app = Flask(__name__)

app_helper = AppHelper(app)

home_page.add_home_page(app, app_helper.prom_metrics, app_helper.configs)
photo_page.add_photo_page(app, app_helper.prom_metrics, app_helper.configs)
sync_status.add_sync_status_pages(app, app_helper.icloud_helper, app_helper.configs, app_helper.sync_handler)
settings_page.add_settings_pages(app, app_helper.prom_metrics, app_helper.configs, app_helper.icloud_helper)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

LOG_LEVEL = str(os.getenv("LOG_LEVEL", "INFO"))
if LOG_LEVEL == "DEBUG":
    print("Logging set to: " + LOG_LEVEL)
    app.logger.setLevel(logging.DEBUG)
elif LOG_LEVEL == "INFO":
    print("Logging set to: " + LOG_LEVEL)
    app.logger.setLevel(logging.INFO)
elif LOG_LEVEL == "WARNING":
    print("Logging set to: " + LOG_LEVEL)
    app.logger.setLevel(logging.WARNING)
elif LOG_LEVEL == "ERROR":
    print("Logging set to: " + LOG_LEVEL)
    app.logger.setLevel(logging.ERROR)
elif LOG_LEVEL == "CRITICAL":
    print("Logging set to: " + LOG_LEVEL)
    app.logger.setLevel(logging.CRITICAL)
else:
    print("ERROR: Unknown Logging level, level set to: INFO")
    app.logger.setLevel(logging.INFO)
