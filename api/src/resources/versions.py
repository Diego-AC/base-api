from src.schemas.versions import VersionSerializer, PayloadVersionSchema
from werkzeug.exceptions import NotFound
from src.resources.base.custom_resource import BaseResource
from src.core.authentication import login_required
from src.repositories.versions import VersionRepository
from src.core.responses import APIResponse
from src.core.logger import logger
from flask import request


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
