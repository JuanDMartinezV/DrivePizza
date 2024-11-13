from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.models.order import Order
from app.domain.schemas.order import OrderCreate, Order as OrderSchema
from app.domain.models.product import PRODUCT_PRICES, get_product_price
from typing import List
import json

router = APIRouter()

@router.post("/", response_model=OrderSchema)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        # Validar productos y calcular total
        total = 0
        for item in order.items:
            try:
                price = get_product_price(item.product)
                total += price * item.quantity
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error en el producto: {str(e)}"
                )

        # Convertir items a JSON string
        items_json = json.dumps([{
            "product": item.product,
            "quantity": item.quantity
        } for item in order.items])
        
        # Crear la orden
        db_order = Order(
            client=order.client,
            items=items_json,
            total=total,
            status="pending"
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Convertir el JSON string de vuelta a lista para la respuesta
        db_order.items = json.loads(db_order.items)
        return db_order
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al crear la orden: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[OrderSchema])
def get_active_orders(db: Session = Depends(get_db)):
    """
    Obtiene la lista de pedidos activos (no cancelados).
    """
    try:
        orders = db.query(Order).filter(Order.status != "cancelled").all()
        
        # Convertir items de JSON a lista para cada orden
        for order in orders:
            order.items = json.loads(order.items)

        return orders

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los pedidos: {str(e)}"
        )

# Agregar un endpoint para obtener los productos disponibles
@router.get("/products")
def get_available_products():
    return {
        "products": [
            {"name": product, "price": price}
            for product, price in PRODUCT_PRICES.items()
        ]
    }

@router.delete("/{order_id}", response_model=OrderSchema)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    try:
        # Buscar la orden
        order = db.query(Order).filter(Order.id == order_id).first()
        
        # Verificar si la orden existe
        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Orden con ID {order_id} no encontrada"
            )
        
        # Eliminar la orden
        db.delete(order)
        db.commit()
        
        # Convertir items de JSON string a lista para la respuesta
        order.items = json.loads(order.items)
        return order
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al eliminar la orden: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Alternativa: Cancelar orden en lugar de eliminarla
@router.put("/{order_id}/cancel", response_model=OrderSchema)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    try:
        # Buscar la orden
        order = db.query(Order).filter(Order.id == order_id).first()
        
        # Verificar si la orden existe
        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Orden con ID {order_id} no encontrada"
            )
            
        # Verificar si la orden ya está cancelada
        if order.status == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="La orden ya está cancelada"
            )
        
        # Actualizar el estado a cancelado
        order.status = "cancelled"
        db.commit()
        db.refresh(order)
        
        # Convertir items de JSON string a lista para la respuesta
        order.items = json.loads(order.items)
        return order
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al cancelar la orden: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all", response_model=List[OrderSchema])
def get_all_orders(db: Session = Depends(get_db)):
    """
    Obtiene todas las órdenes, independientemente de su estado.
    """
    try:
        orders = db.query(Order).all()
        
        # Convertir items de JSON a lista para cada orden
        for order in orders:
            order.items = json.loads(order.items)

        return orders

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener todas las órdenes: {str(e)}"
        )