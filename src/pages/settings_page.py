""" Code to home web page """
from flask import render_template, request, redirect, url_for, abort
from src.helpers.settings import Settings # pylint: disable=import-error
from src.helpers.icloud import ICloud # pylint: disable=import-error

def add_settings_pages(app, configs:Settings, icloud_helper:ICloud):
    """ Add Settings Page """
    @app.route("/settings", methods=['GET', 'POST'])
    def settings_page():
        """ Settings Page """
        if (request.method == 'POST' and
            request.form['photo_location'] != "" and
            request.form['cookie_location'] != "" and
            request.form['watch_interval'] != "" and
            request.form['icloud_album_name'] != ""):
            configs.photo_location = request.form['photo_location']
            configs.cookie_location = request.form['cookie_location']
            configs.watch_interval = request.form['watch_interval']
            configs.icloud_album_name = request.form['icloud_album_name']
            configs.save_settings()
            return redirect(url_for('home_page'))

        return render_template('settings.html', Configs=configs, ICloud=icloud_helper)

    @app.route("/settings/login", methods=['POST'])
    def settings_login_page():
        """ Login Save Page """
        if not (request.form['user'] != "" and request.form['pass'] != ""):
            return render_template(
                'settings.html',
                Configs=configs,
                ICloud=icloud_helper,
                ICloud_error="iCloud Credenials Not Provided")
        configs.username = request.form['user']
        configs.save_settings()
        icloud_helper.update_login(request.form['pass'])
        if not icloud_helper.auth_passed:
            return render_template(
                'settings.html',
                Configs=configs,
                ICloud=icloud_helper,
                ICloud_error="iCloud Login Failed")
        if icloud_helper.needs_2fa_setup:
            return redirect(url_for('settings_2fa_device_page'))
        return redirect(url_for('settings_page'))

    @app.route("/settings/2fa")
    def settings_2fa_device_page():
        """ 2FA Page """
        return render_template('2fa_select.html', Devices=icloud_helper.get_trusted_devices())

    @app.route("/settings/2fa/<int:device>")
    def settings_2fa_request_page(device):
        """ 2FA Page """
        if not icloud_helper.send_2fa_code(device):
            return render_template(
                '2fa_select.html',
                Devices=icloud_helper.get_trusted_devices(),
                O2fa_error="Send 2fa Code Failed")
        return render_template(
            '2fa_input.html', 
            device_id=device, device_name=icloud_helper.describe_trusted_device(device))

    @app.route("/settings/2fa/submit", methods=['POST'])
    def settings_2fa_submit_page():
        """ 2FA Page """
        if (request.method == 'POST' and
            request.form['device_id'] != "" and
            request.form['code'] != ""):
            if icloud_helper.validate_2fa_code(
                int(request.form['device_id']),
                request.form['code']):
                return redirect(url_for('settings_page'))
        return redirect(url_for('settings_2fa_device_page'))
