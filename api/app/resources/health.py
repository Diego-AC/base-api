from ..core.responses import APIResponse
from .base.custom_resource import BaseResource


class HealthResource(BaseResource):
    def get(self):
        return APIResponse.success()