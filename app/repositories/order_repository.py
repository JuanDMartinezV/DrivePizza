from sqlalchemy.orm import Session
from ..domain import models, schemas

class OrderRepository:
    def create(self, db: Session, order: schemas.OrderCreate):
        db_order = models.Order(**order.dict())
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    def get_active(self, db: Session):
        return db.query(models.Order).filter(models.Order.status == "active").all()

    def get_by_id(self, db: Session, order_id: int):
        return db.query(models.Order).filter(models.Order.id == order_id).first()

    def update_status(self, db: Session, order_id: int, status: str):
        order = self.get_by_id(db, order_id)
        if order:
            order.status = status
            db.commit()
            db.refresh(order)
        return order

    def delete(self, db: Session, order_id: int):
        order = self.get_by_id(db, order_id)
        if order:
            db.delete(order)
            db.commit()
        return order 