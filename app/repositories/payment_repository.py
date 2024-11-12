from sqlalchemy.orm import Session
from ..domain import models, schemas
from datetime import datetime

class PaymentRepository:
    def create(self, db: Session, payment: schemas.PaymentCreate):
        db_payment = models.Payment(**payment.dict())
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment

    def get_today(self, db: Session):
        today = datetime.now().date()
        return db.query(models.Payment).filter(
            models.Payment.date >= today
        ).all()

    def get_by_id(self, db: Session, payment_id: int):
        return db.query(models.Payment).filter(models.Payment.id == payment_id).first()

    def delete(self, db: Session, payment_id: int):
        payment = self.get_by_id(db, payment_id)
        if payment:
            db.delete(payment)
            db.commit()
        return payment 