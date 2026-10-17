import os


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'postgresql://user:password@host:5432/dbname',
    )

    SECRET_KEY = os.environ.get('SECRET_KEY', '')

    CORS_ALLOWED_ORIGINS = [
        o.strip()
        for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
        if o.strip()
    ]

    RATELIMIT_ENABLED = (
        os.environ.get('RATELIMIT_ENABLED', 'false').lower() == 'true'
    )
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per minute')
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    LOGGER_NAME = 'app'


class DevConfig(BaseConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'postgresql://{}:{}@{}:{}/{}'.format(
            'postgres',
            'pgpassword',
            'postgres',
            '5432',
            os.getenv('POSTGRES_DB', 'sample'),
        ),
    )

    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:8080',
    ]


class ProdConfig(BaseConfig):
    SQLALCHEMY_ECHO = False
