from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrderBase(BaseModel):
    client: str
    products: str
    total: float
    status: str = "pending"

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

class ReservationBase(BaseModel):
    client: str
    date: datetime
    table_number: int
    status: str = "active"

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    order_id: int
    amount: float
    status: str = "completed"

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True 