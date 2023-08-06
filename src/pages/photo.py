""" Code to home web page """

def add_photo_page(app):
    """ Add Home Page """
    @app.route("/photo")
    @app.route('/photo/<int:refresh>')
    def photo_page(refresh=900):
        """ Photo Page """
        return "<p>Photo page to go here! <br> Refresh is: " + str(refresh) + "</p>"
