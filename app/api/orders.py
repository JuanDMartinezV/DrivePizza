from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..domain import schemas
from ..repositories.order_repository import OrderRepository

router = APIRouter()
order_repository = OrderRepository()

@router.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return order_repository.create(db, order)

@router.get("/orders/active/", response_model=list[schemas.Order])
def get_active_orders(db: Session = Depends(get_db)):
    return order_repository.get_active(db)

@router.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = order_repository.get_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = order_repository.update_status(db, order_id, status)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = order_repository.delete(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted"} 