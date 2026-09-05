from flask import Flask
from flask_restful import Api
from .config import DevConfig
from .extensions import db, migrate, ma
from .routes import register_routes
from .core.errorhandlers import ApiError


class CustomApi(Api):
    @ApiError.error_handler_resources
    def handle_error(self, err):
        raise err

def runserver():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    api = CustomApi(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)


    register_routes(api)
    # register_error_handlers(app)

    return app

