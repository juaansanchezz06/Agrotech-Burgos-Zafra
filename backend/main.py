from fastapi import FastAPI
from .database import engine
from . import models

app = FastAPI(title="Agrotech API")

# Intentamos crear las tablas al iniciar la aplicación de forma controlada
@app.on_event("startup")
def startup_event():
    try:
        print("Conectando a la base de datos en la nube...")
        models.Base.metadata.create_all(bind=engine)
        print("¡Tablas creadas o verificadas con éxito!")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")

@app.get("/")
def read_root():
    return {"status": "ok", "mensaje": "API operativa y Base de Datos en la nube"}