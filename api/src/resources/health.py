from src.core.responses import APIResponse
from src.resources.base.custom_resource import BaseResource


class HealthResource(BaseResource):
    def get(self):
        return APIResponse.success()