from flask_restful import Api
from .resources.health import HealthResource
from .resources.versions import VersionResource, LastVersionResource

def register_routes(api: Api):
    # Registrar los recursos (endpoints) aquí
    api.add_resource(HealthResource, '/') # Endpoint para la lista de ejemplos (GET, POST)
    
    api.add_resource(LastVersionResource, '/versions/last')
    api.add_resource(VersionResource, '/versions')

    return api