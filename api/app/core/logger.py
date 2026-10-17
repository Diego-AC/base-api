import logging
import sys

# Filtro personalizado para niveles específicos
class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        # Permitir solo registros que coincidan con el nivel especificado
        return record.levelno == self.level

# Logger principal. El nombre es provisional: setup.py lo ajusta al valor de
# `app.config['LOGGER_NAME']` después de cargar la config, para que cada
# proyecto pueda identificar sus logs sin leer de env (ver BaseConfig.LOGGER_NAME).
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.propagate = False

# Limpiar handlers existentes
logger.handlers = []

# Handler 1: Formato simple para INFO
console_handler1 = logging.StreamHandler(sys.stdout)
console_handler1.setLevel(logging.INFO)
formatter1 = logging.Formatter("\033[32m%(message)s\033[0m")
console_handler1.setFormatter(formatter1)
console_handler1.addFilter(LevelFilter(logging.INFO))  # Filtra solo INFO

# Handler 2: Formato detallado para ERROR
console_handler2 = logging.StreamHandler(sys.stdout)
console_handler2.setLevel(logging.ERROR)
formatter2 = logging.Formatter(
    "\n\033[41m\033[97m%(levelname)s in %(file_path)s Line: %(line_number)d:\033[0m \033[31m\n%(message)s\033[0m\n"
)
# Defaults para que no truene cuando un call site no pase `extra={'file_path': ..., 'line_number': ...}`.
# `errorhandlers.py` los pasa, pero cualquier logger.error("...") suelto no deberia romper el formateo.
formatter2.default_msec_format = '%s.%03d'
# Python <3.10 no soporta `defaults=` en Formatter; usamos un Filter que rellena los extras faltantes.
class _MissingExtrasFilter(logging.Filter):
    def filter(self, record):
        if not getattr(record, 'file_path', None):
            record.file_path = record.pathname
        if not getattr(record, 'line_number', None):
            record.line_number = record.lineno
        return True
console_handler2.addFilter(_MissingExtrasFilter())
console_handler2.setFormatter(formatter2)
console_handler2.addFilter(LevelFilter(logging.ERROR))  # Filtra solo ERROR

# Agregar handlers al logger
logger.addHandler(console_handler1)
logger.addHandler(console_handler2)

