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
            request.form['user'] != "" and
            request.form['pass'] != ""):
            configs.photo_location = request.form['photo_location']
            if configs.username != request.form['user']:
                configs.username = request.form['user']
                configs.save_settings()
                icloud_helper.update_username()
            else:
                configs.save_settings()
            return redirect(url_for('home_page'))

        return render_template('settings.html', Configs=configs, ICloud=icloud_helper)

    @app.route("/settings/2fa")
    def settings_2fa_device_page():
        """ 2FA Page """
        return render_template('2fa_select.html', Devices=icloud_helper.get_trusted_devices())

    @app.route("/settings/2fa/<int:device>")
    def settings_2fa_request_page(device):
        """ 2FA Page """
        if icloud_helper.send_2fa_code(device):
            abort(404)
        return render_template(
            '2fa_input', 
            device_id=device, device_name=icloud_helper.describe_trusted_device(device))

    @app.route("/settings/2fa/submit")
    def settings_2fa_submit_page():
        """ 2FA Page """
        pass
