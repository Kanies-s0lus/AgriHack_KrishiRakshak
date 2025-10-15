from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'key here'  #Generate and add a Secret key here when deploying



    from app import routes
    app.register_blueprint(routes.bp)

    return app