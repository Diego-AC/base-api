import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from .config import DevConfig, ProdConfig
from .extensions import db, migrate, ma
from . import auth  # noqa: F401 — registers backends at import time
from .routes import register_routes
from .core.errorhandlers import normalize_error
from .core.logger import logger as _base_logger


class CustomApi(Api):
    def handle_error(self, e):
        return normalize_error(e)


def register_error_handlers(app):
    app.register_error_handler(HTTPException, lambda e: normalize_error(e))
    app.register_error_handler(Exception, lambda e: normalize_error(e))


def _bind_logger_name(app):
    """Re-registra el logger base con el nombre que la config define.

    El logger se crea en import-time con un nombre provisional. Acá, una vez
    cargada la config, lo movemos al nombre del proyecto para que cada fork
    pueda identificar sus logs en agregadores externos (Kibana, Datadog, etc.)
    sin tener que leer de env. Los handlers y filtros se conservan.
    """
    from .core import logger as _logger_module
    new_name = app.config.get('LOGGER_NAME', 'app')
    fresh = logging.getLogger(new_name)
    fresh.setLevel(_base_logger.level)
    fresh.propagate = _base_logger.propagate
    fresh.handlers = list(_base_logger.handlers)
    _logger_module.logger = fresh


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

    _bind_logger_name(app)

    register_routes(api)
    register_error_handlers(app)

    return app
