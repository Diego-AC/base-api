from sqlalchemy import asc, desc
from sqlalchemy.orm import Query
from collections import namedtuple
from typing import Type, Optional

from ...extensions import db

OrderBy = namedtuple("OrderBy", ["key", "asc"])
Paginate = namedtuple("Paginate", ["page", "per_page"])


class BaseRepository:
    """
    Helper concreto para repositorios. No define contrato.

    Esta base NO usa `ABC` ni `@abstractmethod` a propósito: una plantilla
    reutilizable no puede fijar la firma de `create` o `get_or_create`,
    porque cada dominio legítimo pide parámetros distintos (commit/flush,
    eventos, dry-run, side-effects, etc.). Forzar el contrato rompe forks.

    La base expone lo que sí sabe hacer de forma estable:
    - acceso a `query` y al modelo
    - lectura: `get`, `get_or_fail`, `get_all`
    - escritura genérica: `update`, `delete` (soft-delete via el mixin)
    - helpers internos: filtro, orden, paginación

    `create` y `get_or_create` se dejan como métodos concretos que delegan
    al modelo. Cada repo concreto los puede override con la firma que su
    dominio pida, o dejarlos como están si el default le sirve. La firma
    concreta la define el repo, NO el template (ver AGENTS.md R14).
    """

    model: Type[db.Model]

    @property
    def query(self):
        return self.model.query

    def get(self, _id):
        return self.query.get(_id)

    def get_or_fail(self, _id):
        return self.query.filter_by(id=_id).first_or_404()

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

    def create(self, **kwargs):
        """
        Default genérico: instancia el modelo con los kwargs recibidos y
        persiste via el mixin `save()`. Override en el repo concreto si
        tu dominio necesita más control (commit explícito, eventos,
        validaciones previas, etc.). Ver AGENTS.md R14.
        """
        entity = self.model(**kwargs)
        entity.save()
        return entity

    def get_or_create(self, defaults=None, **kwargs):
        """
        Default genérico: busca por los kwargs; si no existe, lo crea
        mezclando `defaults` con los kwargs de búsqueda. Override en el
        repo concreto si tu dominio lo necesita distinto. Ver AGENTS.md R14.
        """
        instance = self.query.filter_by(**kwargs).first()
        if instance:
            return instance, False
        params = {**(defaults or {}), **kwargs}
        instance = self.model(**params)
        instance.save()
        return instance, True

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
