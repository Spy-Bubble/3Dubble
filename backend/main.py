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

class MensajeHistorial(BaseModel):
    remitente: str
    texto: str

class MensajeCliente(BaseModel):
    texto: str
    historial: list[MensajeHistorial] = []

def obtener_conexion():
    # Esta línea calcula la ruta exacta hacia la carpeta 'backend' de forma automática
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
    conexion = sqlite3.connect('backend/inventario3d.db')
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    # =====================================================================
    # FASE 1: AGENTE 1 (El Ruteador / Analista Multi-Categoría)
    # =====================================================================
    mensajes_analista = [
        {
            'role': 'system',
            'content': '''Tu único objetivo es clasificar la intención de la ÚLTIMA pregunta del usuario basándote en el contexto de la conversación.
            
            1. Determina la CATEGORIA exacta: FILAMENTOS, IMPRESORAS o ACCESORIOS.
            2. Extrae las PALABRAS clave (marcas, modelos o componentes). Si el usuario dice "esa impresora" o "para ella", busca en el historial de qué modelo están hablando y extrae ese nombre real.
            
            Formato de respuesta ESTRICTO (Cero explicaciones, responde solo una línea con este molde):
            CATEGORIA: <CATEGORIA> | PALABRAS: <palabras_separadas_por_comas>'''
        }
    ]
    
    # Le inyectamos los últimos 2 mensajes para que entienda a qué se refiere "esa impresora"
    for msg in mensaje.historial[-2:]:
        rol = 'assistant' if msg.remitente == 'agente' else 'user'
        mensajes_analista.append({'role': rol, 'content': msg.texto})
        
    # Agregamos la petición actual
    mensajes_analista.append({ 'role': 'user', 'content': mensaje.texto })

    respuesta_analista = ollama.chat(model='gemma4:latest', messages=mensajes_analista)
    
    # Extraemos la línea de texto del Agente 1 y la procesamos
    linea_analisis = respuesta_analista['message']['content'].strip()
    print(f"⚙️ [Agente 1 Telemetría]: {linea_analisis}")
    
    categoria = "FILAMENTOS"
    palabras_crudas = ""
    
    if "|" in linea_analisis:
        partes = linea_analisis.split("|")
        categoria = partes[0].replace("CATEGORIA:", "").strip().upper()
        palabras_crudas = partes[1].replace("PALABRAS:", "").strip()

    # =====================================================================
    # FASE 2: Mapeo de Tablas y Columnas en SQLite según la Categoría
    # =====================================================================
    if "IMPRESORAS" in categoria:
        tabla = "impresoras"
        columnas_busqueda = ["marca", "modelo", "volumen_impresion"]
        # Columnas específicas que tiene la tabla impresoras
        columnas_select = ["marca", "modelo", "volumen_impresion", "precio", "stock"]
    elif "ACCESORIOS" in categoria:
        tabla = "accesorios"
        columnas_busqueda = ["nombre", "compatibilidad"]
        # Columnas específicas de la tabla accesorios
        columnas_select = ["nombre", "compatibilidad", "precio", "stock"]
    else:
        tabla = "filamentos"
        columnas_busqueda = ["marca", "material", "color"]
        columnas_select = ["marca", "material", "color", "precio", "stock"]

    # =====================================================================
    # FASE 3: Construcción de la Consulta SQL Dinámica (Buscador Avanzado)
    # =====================================================================
    palabras_limpias = palabras_crudas.replace(',', ' ').replace('.', ' ')
    palabras_clave = [p.strip() for p in palabras_limpias.split() if len(p.strip()) > 1]
    
    # Palabras de "ruido" que no queremos buscar literalmente en la base de datos
    palabras_ignoradas = ['refaccion', 'componente', 'accesorio', 'impresora', 'filamento', 'tienes', 'hay', 'busco']
    palabras_clave_filtradas = [p for p in palabras_clave if p.lower() not in palabras_ignoradas]

    condiciones = []
    parametros = []
    
    for palabra in palabras_clave_filtradas:
        condiciones_por_palabra = [f"{col} LIKE ?" for col in columnas_busqueda]
        condiciones.append(f"({' OR '.join(condiciones_por_palabra)})")
        parametros.extend([f"%{palabra}%"] * len(columnas_busqueda))

    query = f"SELECT {', '.join(columnas_select)} FROM {tabla}"
    
    # Si logramos extraer palabras específicas (ej. "Snapmaker", "Boquilla"), buscamos exacto
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones) 
    # Si la pregunta fue genérica (ej. "tienes accesorios?"), traemos una muestra aleatoria
    else:
        query += " ORDER BY RANDOM()"
        
    query += " LIMIT 12" 
    
    cursor.execute(query, parametros)
    resultados = cursor.fetchall()
    conexion.close()
    
    if not resultados:
        datos_crudos = f"No se encontraron registros en la tabla '{tabla}' que coincidan con los criterios."
    else:
        datos_crudos = f"DATOS DE INVENTARIO REAL ({tabla.upper()}):\n"
        for f in resultados:
            detalles = [f"{col}: {f[col]}" for col in columnas_select]
            datos_crudos += f"- " + " | ".join(detalles) + "\n"

    # =====================================================================
    # FASE 4: AGENTE 3 (El Asesor de Ventas Final con contexto total)
    # =====================================================================
    
    # 1. Instrucción base y datos de inventario
    mensajes_agente = [
        {
            'role': 'system',
            'content': f'''Eres el Agente de Soporte y Ventas de 3Dubble. 
            Responde las dudas técnicas o comerciales del cliente de forma concisa, persuasiva y profesional.
            
            Usa EXCLUSIVAMENTE estos datos extraídos de la base de datos para tu respuesta:
            {datos_crudos}
            
            Si la base de datos muestra que un producto tiene stock, intenta cerrar la venta. Si no hay stock, ofrece alternativas válidas dentro de lo disponible.'''
        }
    ]
    
    # 2. Inyectamos los últimos 4 mensajes del historial para darle memoria (evita saturar la RAM)
    for msg in mensaje.historial[-4:]:
        rol = 'assistant' if msg.remitente == 'agente' else 'user'
        mensajes_agente.append({'role': rol, 'content': msg.texto})
        
    # 3. Agregamos la pregunta actual del cliente
    mensajes_agente.append({'role': 'user', 'content': mensaje.texto})

    respuesta_final = ollama.chat(model='gemma4:latest', messages=mensajes_agente)
    return {"respuesta": respuesta_final['message']['content']}