from flask_restful import Api

from .resources.health import HealthResource, ReadinessResource
from .resources.versions import LastVersionResource, VersionResource


def register_routes(api: Api):
    api.add_resource(HealthResource, '/')
    api.add_resource(ReadinessResource, '/health')
    api.add_resource(LastVersionResource, '/versions/last')
    api.add_resource(VersionResource, '/versions')
    return api
