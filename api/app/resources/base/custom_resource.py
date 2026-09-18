from flask_restful import Resource

from ...core.errorhandlers import wrap_resource


class BaseResource(Resource):
    @wrap_resource
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
