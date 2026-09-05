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

# Logger principal
logger = logging.getLogger("multi_console_logger")
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
console_handler2.setFormatter(formatter2)
console_handler2.addFilter(LevelFilter(logging.ERROR))  # Filtra solo ERROR

# Agregar handlers al logger
logger.addHandler(console_handler1)
logger.addHandler(console_handler2)

