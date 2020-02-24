# third-party imports
import os
import atexit

from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
from .scheduled_jobs import Jobs
from flask import Flask

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()
login_manager = LoginManager()
scheduler = BackgroundScheduler()
jobs = Jobs()


def create_app(config_name):
    app_dir = os.path.dirname(__file__)
    app = Flask(__name__, instance_path=os.path.dirname(app_dir) + '/instance', instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"

    migrate = Migrate(app, db)
    Bootstrap(app)

    if scheduler.running:
        scheduler.shutdown()
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    from app import models

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .client import client as client_blueprint
    app.register_blueprint(client_blueprint)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .student import student as student_blueprint
    app.register_blueprint(student_blueprint)

    from .staff import staff as staff_blueprint
    app.register_blueprint(staff_blueprint)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', title='Forbidden'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', title='Server Error'), 500

    return app
