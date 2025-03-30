from .base.mixins import BaseRepository
from src.models import Version
from src.extensions import db

class VersionRepository(BaseRepository):
	def __init__(self):
		self.model = Version

	def get_last(self):
		return self.query.order_by(self.model.id.desc()).first()
	
	def create(self, dataJson):
		entity = self.model(
			description=dataJson.get("description"),
			status=dataJson.get("status", 0),
		)
		entity.save()
		return entity.id