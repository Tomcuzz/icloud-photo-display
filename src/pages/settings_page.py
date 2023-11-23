""" Code to home web page """
from flask import render_template, request, redirect, url_for
from src.helpers.app import AppHelper # pylint: disable=import-error

def add_settings_pages(app, app_helper:AppHelper):
    """ Add Settings Page """
    @app.route("/settings", methods=['GET', 'POST'])
    def settings_page():
        """ Settings Page """
        if (request.method == 'POST' and
            request.form['all_photo_location'] != "" and
            request.form['photo_location'] != "" and
            request.form['cookie_directory'] != "" and
            request.form['all_watch_interval'] != "" and
            request.form['watch_interval'] != "" and
            request.form['icloud_album_name'] != ""):
            app_helper.configs.all_photo_location = request.form['all_photo_location']
            app_helper.configs.photo_location = request.form['photo_location']
            app_helper.configs.cookie_directory = request.form['cookie_directory']
            app_helper.configs.all_watch_interval = int(request.form['all_watch_interval'])
            app_helper.configs.watch_interval = int(request.form['watch_interval'])
            if app_helper.icloud_helper.is_authed \
                and app_helper.icloud_helper.photo_album_exists(request.form['icloud_album_name']):
                app_helper.configs.icloud_album_name = request.form['icloud_album_name']
                app_helper.configs.save_settings()
            else:
                app_helper.configs.save_settings()
                return render_template(
                    'settings.html',
                    configs=app_helper.configs,
                    ICloud=app_helper.icloud_helper,
                    Settings_error="iCloud Album Doesn't exist")
            return redirect(url_for('home_page'))
        elif request.method == 'POST':
            return render_template(
                'settings.html',
                configs=app_helper.configs,
                ICloud=app_helper.icloud_helper,
                Settings_error="A Required Field Was Not Provided")

        return render_template(
            'settings.html',
            configs=app_helper.configs,
            ICloud=app_helper.icloud_helper)

    @app.route("/settings/login", methods=['POST'])
    def settings_login_page():
        """ Login Save Page """
        if not (request.form['user'] != "" and request.form['pass'] != ""):
            return render_template(
                'settings.html',
                configs=app_helper.configs,
                ICloud=app_helper.icloud_helper,
                ICloud_error="iCloud Credenials Not Provided")
        app_helper.configs.username = request.form['user']
        app_helper.configs.save_settings()
        app_helper.icloud_helper.update_login(request.form['pass'])
        if not app_helper.icloud_helper.has_password:
            return render_template(
                'settings.html',
                configs=app_helper.configs,
                ICloud=app_helper.icloud_helper,
                ICloud_error="iCloud Login Failed")
        if app_helper.icloud_helper.needs_2fa_setup:
            return redirect(url_for('settings_2fa_device_page'))
        return redirect(url_for('settings_page'))

    @app.route("/settings/2fa")
    def settings_2fa_device_page():
        """ 2FA Page """
        return render_template('2fa_select.html', Devices=app_helper.icloud_helper.get_trusted_devices())

    @app.route("/settings/2fa/<int:device>")
    def settings_2fa_request_page(device):
        """ 2FA Page """
        if not app_helper.icloud_helper.send_2fa_code(device):
            return render_template(
                '2fa_select.html',
                Devices=app_helper.icloud_helper.get_trusted_devices(),
                O2fa_error="Send 2fa Code Failed")
        return render_template(
            '2fa_input.html', 
            device_id=device, device_name=app_helper.icloud_helper.describe_trusted_device(device))

    @app.route("/settings/2fa/submit", methods=['POST'])
    def settings_2fa_submit_page():
        """ 2FA Page """
        if (request.method == 'POST' and
            request.form['device_id'] != "" and
            request.form['code'] != ""):
            if app_helper.icloud_helper.validate_2fa_code(
                int(request.form['device_id']),
                request.form['code']):
                return redirect(url_for('settings_page'))
        return redirect(url_for('settings_2fa_device_page'))
