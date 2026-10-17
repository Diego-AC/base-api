from .base.mixins import BaseRepository
from ..models import Version

class VersionRepository(BaseRepository):
	def __init__(self):
		self.model = Version

	def get_last(self):
		return self.query.order_by(self.model.id.desc()).first()
	
	def create(self, dataJson):
		entity = self.model(
			description=dataJson.get("description"),
			active=dataJson.get("active", True),
		)
		entity.save()
		return entity.id