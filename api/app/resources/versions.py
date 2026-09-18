from ..schemas.versions import VersionSerializer, PayloadVersionSchema

from .base.custom_resource import BaseResource
from ..core.authentication import login_required
from ..repositories.versions import VersionRepository
from ..core.responses import APIResponse
from ..core.logger import logger
from flask import request
from werkzeug.exceptions import NotFound


repository = VersionRepository()
serializer = VersionSerializer()


class LastVersionResource(BaseResource):
    def get(self):
        last_version = repository.get_last()
        if last_version is None:
            raise NotFound(description="The requested item was not found.")
        data = serializer.dump(last_version)

        return APIResponse.success(data=data)
    
    
class VersionResource(BaseResource):
    @login_required
    def post(self):
        schema = PayloadVersionSchema()

        payload = request.get_json()
        schema.load(payload)
        id = repository.create(payload)

        return APIResponse.success(data={"id": id}, status=201)
