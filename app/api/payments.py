from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..domain import schemas
from ..repositories.payment_repository import PaymentRepository

router = APIRouter()
payment_repository = PaymentRepository()

@router.post("/payments/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return payment_repository.create(db, payment)

@router.get("/payments/today/", response_model=list[schemas.Payment])
def get_today_payments(db: Session = Depends(get_db)):
    return payment_repository.get_today(db)

@router.get("/payments/{payment_id}", response_model=schemas.Payment)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = payment_repository.get_by_id(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = payment_repository.delete(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted"} 