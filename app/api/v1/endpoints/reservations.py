from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.models.reservation import Reservation
from app.domain.schemas.reservation import ReservationCreate, Reservation as ReservationSchema
from typing import List
from datetime import datetime, date, time

router = APIRouter()

@router.post("/", response_model=ReservationSchema)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    try:
        # Asegurarse de que la fecha y la hora sean objetos de tipo date y time
        db_reservation = Reservation(
            date=reservation.date,  # Esto ya es un objeto date
            time=reservation.time,  # Esto ya es un objeto time
            people_count=reservation.people_count,
            client_name=reservation.client_name
        )
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ReservationSchema])
def get_reservations(db: Session = Depends(get_db)):
    """
    Obtiene la lista de reservas, ordenadas por fecha y hora.
    """
    try:
        reservations = db.query(Reservation).order_by(Reservation.date, Reservation.time).all()
        
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las reservas: {str(e)}")

@router.get("/all", response_model=List[ReservationSchema])
def get_all_reservations(db: Session = Depends(get_db)):
    """
    Obtiene todas las reservas, independientemente de su estado.
    """
    try:
        reservations = db.query(Reservation).all()
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener todas las reservas: {str(e)}")
