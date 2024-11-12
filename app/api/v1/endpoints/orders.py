from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.domain.models.order import Order
from app.domain.schemas.order import OrderCreate, Order as OrderSchema
from app.domain.models.product import PRODUCT_PRICES, get_product_price
from typing import List, Optional
from datetime import datetime
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
def get_orders(
    status: Optional[str] = Query(None, description="Filtrar por estado (pending, completed, cancelled)"),
    client: Optional[str] = Query(None, description="Filtrar por nombre del cliente"),
    date_from: Optional[datetime] = Query(None, description="Filtrar desde fecha (YYYY-MM-DD)"),
    date_to: Optional[datetime] = Query(None, description="Filtrar hasta fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de pedidos con opciones de filtrado.
    """
    try:
        # Iniciar la consulta
        query = db.query(Order)

        # Aplicar filtros si se proporcionan
        if status:
            query = query.filter(Order.status == status)
        if client:
            query = query.filter(Order.client.ilike(f"%{client}%"))
        if date_from:
            query = query.filter(Order.date >= date_from)
        if date_to:
            query = query.filter(Order.date <= date_to)

        # Ordenar por fecha, más recientes primero
        query = query.order_by(Order.date.desc())

        # Ejecutar la consulta
        orders = query.all()

        # Convertir items de JSON a lista para cada orden
        for order in orders:
            order.items = json.loads(order.items)

        return orders

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los pedidos: {str(e)}"
        )

@router.get("/summary")
def get_orders_summary(
    date_from: Optional[datetime] = Query(None, description="Desde fecha (YYYY-MM-DD)"),
    date_to: Optional[datetime] = Query(None, description="Hasta fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen de los pedidos activos (no cancelados).
    """
    try:
        # Iniciar la consulta excluyendo órdenes canceladas
        query = db.query(Order).filter(Order.status != "cancelled")

        # Aplicar filtros de fecha si se proporcionan
        if date_from:
            query = query.filter(Order.date >= date_from)
        if date_to:
            query = query.filter(Order.date <= date_to)

        # Ejecutar la consulta
        orders = query.all()

        # Calcular estadísticas
        total_orders = len(orders)
        total_revenue = sum(order.total for order in orders)
        
        # Contar órdenes por estado (excluyendo canceladas)
        orders_by_status = {}
        
        # Contar productos más vendidos
        product_counts = {}
        for order in orders:
            # Contar por estado
            status = order.status
            if status not in orders_by_status:
                orders_by_status[status] = 0
            orders_by_status[status] += 1
            
            # Contar productos
            items = json.loads(order.items)
            for item in items:
                product = item['product']
                quantity = item['quantity']
                if product not in product_counts:
                    product_counts[product] = 0
                product_counts[product] += quantity

        # Ordenar productos por cantidad vendida
        top_products = sorted(
            [{"product": k, "quantity": v} for k, v in product_counts.items()],
            key=lambda x: x["quantity"],
            reverse=True
        )[:5]  # Top 5 productos

        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "orders_by_status": orders_by_status,
            "top_products": top_products,
            "date_range": {
                "from": date_from,
                "to": date_to
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el resumen de pedidos: {str(e)}"
        )

@router.get("/cancelled", response_model=List[OrderSchema])
def get_cancelled_orders(
    date_from: Optional[datetime] = Query(None, description="Desde fecha (YYYY-MM-DD)"),
    date_to: Optional[datetime] = Query(None, description="Hasta fecha (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de pedidos cancelados.
    """
    try:
        query = db.query(Order).filter(Order.status == "cancelled")

        if date_from:
            query = query.filter(Order.date >= date_from)
        if date_to:
            query = query.filter(Order.date <= date_to)

        orders = query.order_by(Order.date.desc()).all()

        # Convertir items de JSON a lista para cada orden
        for order in orders:
            order.items = json.loads(order.items)

        return orders

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los pedidos cancelados: {str(e)}"
        )

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