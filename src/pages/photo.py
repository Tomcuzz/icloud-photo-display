""" Code to home web page """

def add_photo_page(app):
    """ Add Home Page """
    @app.route("/photo")
    @app.route('/photo/<refresh>')
    def photo_page(refresh=900):
        """ Photo Page """
        return "<p>Photo page to go here!</p>"
