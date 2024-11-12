from sqlalchemy.orm import Session
from ..domain import models, schemas

class ReservationRepository:
    def create(self, db: Session, reservation: schemas.ReservationCreate):
        db_reservation = models.Reservation(**reservation.dict())
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation

    def get_active(self, db: Session):
        return db.query(models.Reservation).filter(models.Reservation.status == "active").all()

    def get_by_id(self, db: Session, reservation_id: int):
        return db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()

    def update_status(self, db: Session, reservation_id: int, status: str):
        reservation = self.get_by_id(db, reservation_id)
        if reservation:
            reservation.status = status
            db.commit()
            db.refresh(reservation)
        return reservation

    def delete(self, db: Session, reservation_id: int):
        reservation = self.get_by_id(db, reservation_id)
        if reservation:
            db.delete(reservation)
            db.commit()
        return reservation 