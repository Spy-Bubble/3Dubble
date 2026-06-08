from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os # 🔥 Importamos esto para el manejo de rutas

app = FastAPI(title="3Dubble API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_conexion():
    # 🔥 Esta línea calcula la ruta exacta hacia la carpeta 'backend' de forma automática
    ruta_db = os.path.join(os.path.dirname(__file__), "inventario3d.db")
    
    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row 
    return conexion

@app.get("/")
def read_root():
    return {"mensaje": "¡El cerebro de 3Dubble está en línea!"}

@app.get("/api/filamentos")
def obtener_filamentos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM filamentos")
    filamentos = cursor.fetchall()
    
    conexion.close()
    
    return [dict(fila) for fila in filamentos]