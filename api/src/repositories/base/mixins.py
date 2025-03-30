from abc import ABC, abstractmethod
from sqlalchemy import asc, desc
from sqlalchemy.orm import Query
from collections import namedtuple
from typing import Type, Optional

from src.extensions import db

OrderBy = namedtuple("OrderBy", ["key", "asc"])
Paginate = namedtuple("Paginate", ["page", "per_page"])


class BaseRepository(ABC):
    model: Type[db.Model]
    
    @property
    def query(self):
        return self.model.query

    #@abstractmethod
    def get_or_create(self, **kwargs):
        """
        Abstract method to get or create an instance.
        Must be implemented by any class inheriting from RepositoryBase.
        """
        pass

    @abstractmethod
    def create(self, **kwargs):
        """
        Abstract method to create an instance.
        Must be implemented by any class inheriting from RepositoryBase.
        """
        pass

    def get(self, _id):
        return self.query.get(_id)

    def get_or_fail(self, _id):
        return self.query.get_or_404(_id)
    
    def get_all(
        self,
        filters: Optional[dict] = None,
        paginate: Optional[Paginate] = None,
        order_by: OrderBy = OrderBy(key="id", asc=True)
    ):
        query = self.query
        
        if filters:
            query = self._apply_filter(query, filters)
        
        query = self._apply_order(query, order_by)

        if not paginate:
            items = query.all()
            return {
                "items": items,
                "total": len(items)
            }
        return self._paginate_to_dict(
            query.paginate(
                page=paginate.page,
                per_page=paginate.per_page
            )
        )
    
    def update(self, _id, dataJson):
        entity = self.query.get(_id)
        if not entity:
            return None
        dataJson.pop('id', None)

        for key, value in dataJson.items():
            if hasattr(self.model, key):
                setattr(entity, key, value)

        return entity.update()

    def delete(self, _id):
        entity = self.query.get(_id)
        if entity: 
            entity.delete()

    def _apply_filter(self, query: Query, filters: dict = {}):
        filtered = {
            key: value
            for key, value in (filters or {}).items()
            if hasattr(self.model, key)
        }
        return query.filter_by(**filtered)

    def _apply_order(self, query: Query, order_by: Type[OrderBy] = OrderBy(key="id", asc=True)):
        if hasattr(self.model, order_by.key):
            order_func = asc if order_by.asc else desc
            query = query.order_by(
                order_func( getattr(self.model, order_by.key) )
            )
        else:
            query = query.order_by(self.model.id.asc())
        return query
    
    def _paginate_to_dict(self, paginated):
        """Convert the paginated result to a dictionary format."""
        return {
            "items": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "per_page": paginated.per_page,
            "pages": paginated.pages,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev,
        }