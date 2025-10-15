from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'key here'  #Generate and add a Secret key here when deploying
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///krishirakshak.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    from app import routes
    app.register_blueprint(routes.bp)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'routes.login'
    login_manager.login_message = "Please log in first"
    login_manager.login_message_category = 'warning' 
    login_manager.init_app(app)

    from app.models import User  # simple user model
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) 

    return app