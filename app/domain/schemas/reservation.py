from pydantic import BaseModel
from datetime import date, time

class ReservationBase(BaseModel):
    date: date  # Solo la fecha
    time: time  # Solo la hora
    people_count: int
    client_name: str

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True
