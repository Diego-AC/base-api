import os


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'postgresql://pguser:pgpassword@localhost/nombre_base_datos',
    )


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
            'principal',
        ),
    )


class ProdConfig(BaseConfig):
    SQLALCHEMY_ECHO = False

