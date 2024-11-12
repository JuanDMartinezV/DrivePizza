from fastapi import FastAPI
from .database import engine, Base
from .api.v1.router import api_router

app = FastAPI(title="Restaurant API")

# Crear las tablas de la base de datos
Base.metadata.create_all(bind=engine)

# Agregar prints de depuración
print("Rutas disponibles:")
for route in api_router.routes:
    print(f"- {route.path} [{route.methods}]")

# Incluir los routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Restaurant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 