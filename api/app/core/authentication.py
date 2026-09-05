from functools import wraps
from flask import request, g
from werkzeug.exceptions import Forbidden


def login_required(f):
    """ Decorador para validar el token en métodos específicos """
    @wraps(f)
    def auth(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            raise Forbidden() 
        """
        Usar 'g' permite mantener objetos globalmente a lo largo de toda la petición.
        Debe implementarse cuando se definan los modelos de autenticación.
        Por ejemplo:
        g.usuario = {} or SQLalchemy.User
        """

        # g.usuario = {}
        
        return f(*args, **kwargs)
    return auth