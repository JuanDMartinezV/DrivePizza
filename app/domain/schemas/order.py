from pydantic import BaseModel
from datetime import datetime
from typing import List

class OrderItem(BaseModel):
    product: str
    quantity: int

class OrderBase(BaseModel):
    client: str
    items: List[OrderItem]

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    date: datetime
    total: float
    status: str

    class Config:
        from_attributes = True