from sqlalchemy import text

from ..core.responses import APIResponse
from ..extensions import db
from .base.custom_resource import BaseResource


class HealthResource(BaseResource):
    """Liveness: 200 siempre. Usado por Docker para saber si el proceso vive."""

    def get(self):
        return APIResponse.success()


class ReadinessResource(BaseResource):
    """Readiness: 200 solo si la DB responde. Usado por load balancers / healthchecks."""

    def get(self):
        try:
            db.session.execute(text('SELECT 1'))
            return APIResponse.success()
        except Exception as exc:
            return APIResponse.error(
                message=f'Database not ready: {exc}',
                status_code=503,
            )
