import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from .config import DevConfig, ProdConfig
from .extensions import db, migrate, ma
from .routes import register_routes
from .core.errorhandlers import normalize_error


class CustomApi(Api):
    def handle_error(self, e):
        return normalize_error(e)


def register_error_handlers(app):
    app.register_error_handler(HTTPException, lambda e: normalize_error(e))
    app.register_error_handler(Exception, lambda e: normalize_error(e))


def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config_name = os.getenv('FLASK_CONFIG', 'dev')
        if config_name == 'production':
            config = ProdConfig
        else:
            config = DevConfig

    app.config.from_object(config)
    if hasattr(config, 'init_app'):
        config.init_app(app)

    CORS(app, origins=app.config.get('CORS_ALLOWED_ORIGINS', []))

    if app.config.get('RATELIMIT_ENABLED'):
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        limiter = Limiter(
            get_remote_address,
            app=app,
            default_limits=[app.config['RATELIMIT_DEFAULT']],
            storage_uri=app.config['RATELIMIT_STORAGE_URI'],
        )
        limiter.init_app(app)

    api = CustomApi(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    register_routes(api)
    register_error_handlers(app)

    return app
