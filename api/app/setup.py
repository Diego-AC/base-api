from flask import Flask
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from .config import DevConfig
from .extensions import db, migrate, ma
from .routes import register_routes
from .core.errorhandlers import normalize_error


class CustomApi(Api):
    def handle_error(self, e):
        return normalize_error(e)


def register_error_handlers(app):
    app.register_error_handler(HTTPException, lambda e: normalize_error(e))
    app.register_error_handler(Exception, lambda e: normalize_error(e))


def runserver():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    api = CustomApi(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    register_routes(api)
    register_error_handlers(app)

    return app
