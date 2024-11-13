from sqlalchemy import Column, Integer, String, Date, Time
from app.database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)  # Solo la fecha
    time = Column(Time)  # Solo la hora
    people_count = Column(Integer)  # Cantidad de personas
    client_name = Column(String)  # Nombre del cliente