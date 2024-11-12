from enum import Enum

class ProductEnum(str, Enum):
    PIZZA = "Pizza"
    BURGER = "Hamburguesa"
    SALAD = "Ensalada"
    SODA = "Refresco"
    FRIES = "Papas fritas"

PRODUCT_PRICES = {
    "Pizza": 10.99,
    "Hamburguesa": 8.99,
    "Ensalada": 7.99,
    "Refresco": 1.99,
    "Papas fritas": 3.99
}

def get_product_price(product: str) -> float:
    if product not in PRODUCT_PRICES:
        raise ValueError(f"Producto no válido: {product}. Productos disponibles: {list(PRODUCT_PRICES.keys())}")
    return PRODUCT_PRICES[product] 