from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import ollama
import os

app = FastAPI(title="3Dubble API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MensajeCliente(BaseModel):
    texto: str

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

# (Tu código anterior de obtener_filamentos se queda igual...)

@app.get("/api/impresoras")
def obtener_impresoras():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM impresoras")
    impresoras = cursor.fetchall()
    conexion.close()
    return [dict(fila) for fila in impresoras]

@app.get("/api/accesorios")
def obtener_accesorios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM accesorios")
    accesorios = cursor.fetchall()
    conexion.close()
    return [dict(fila) for fila in accesorios]

@app.post("/api/chat")
def procesar_chat(mensaje: MensajeCliente):
    # 1. Leemos el inventario para dárselo al Agente
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    # Traemos una muestra del inventario para contexto
    cursor.execute("SELECT marca, material, color, precio, stock FROM filamentos LIMIT 30")
    resultados = cursor.fetchall()
    conexion.close()
    
    datos_crudos = "INVENTARIO ACTUAL:\n"
    for f in resultados:
        datos_crudos += f"- {f['marca']} {f['material']} {f['color']} | ${f['precio']} | Stock: {f['stock']}\n"

    # 2. Conectamos con tu modelo local de Ollama
    respuesta = ollama.chat(model='gemma4:latest', messages=[
        {
            'role': 'system',
            'content': f'''Eres el Agente de Soporte y Ventas de 3Dubble. 
            Responde las dudas del cliente de forma muy concisa, persuasiva y amable. 
            Usa ESTOS datos de inventario si te preguntan por filamentos:
            {datos_crudos}'''
        },
        {
            'role': 'user',
            'content': mensaje.texto
        }
    ])
    
    return {"respuesta": respuesta['message']['content']}