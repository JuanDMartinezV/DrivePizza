from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..domain import schemas
from ..repositories.reservation_repository import ReservationRepository

router = APIRouter()
reservation_repository = ReservationRepository()

@router.post("/reservations/", response_model=schemas.Reservation)
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    return reservation_repository.create(db, reservation)

@router.get("/reservations/active/", response_model=list[schemas.Reservation])
def get_active_reservations(db: Session = Depends(get_db)):
    return reservation_repository.get_active(db)

@router.get("/reservations/{reservation_id}", response_model=schemas.Reservation)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = reservation_repository.get_by_id(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.put("/reservations/{reservation_id}/status")
def update_reservation_status(reservation_id: int, status: str, db: Session = Depends(get_db)):
    reservation = reservation_repository.update_status(db, reservation_id, status)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = reservation_repository.delete(db, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"message": "Reservation deleted"} 