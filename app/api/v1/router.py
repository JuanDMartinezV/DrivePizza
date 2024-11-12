from fastapi import APIRouter
from .endpoints import orders

api_router = APIRouter()

# Agregar print de depuración
print("Configurando router de orders...")

api_router.include_router(orders.router, prefix="/orders", tags=["orders"])

# Verificar rutas después de incluir el router
print("Rutas en api_router después de incluir orders:")
for route in api_router.routes:
    print(f"- {route.path}")