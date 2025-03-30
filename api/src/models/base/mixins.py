from src.extensions import db


class TransactionalMixin:
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update(self):
        db.session.commit()
        return self

    def _force_delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def delete(self):
        # Logic delete
        self.status = 0
        db.session.add(self)
        db.session.commit()
        return self


