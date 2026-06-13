from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import ollama
import os
import re

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

def normalizar_notacion_numerica(texto: str):
    # Convierte "10k" a "10000"
    return re.sub(r'(\d+)k', lambda m: str(int(m.group(1)) * 1000), texto, flags=re.IGNORECASE)

def extraer_rango_precio(texto: str):
    texto_norm = normalizar_notacion_numerica(texto)
    # Patrón mejorado para capturar precios
    patron = r'(?:entre|de)?\s*(\d+)\s*(?:a|y|-)\s*(\d+)'
    match = re.search(patron, texto_norm, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None

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
    # AGENTE 1 (El Ruteador / Analista Multi-Categoría)
    # =====================================================================
    mensajes_analista = [
        {
            'role': 'system',
            'content': '''Eres un clasificador de intenciones para una tienda de impresión 3D llamada 3Dubble.

    Tu tarea: analizar la ÚLTIMA pregunta del usuario y extraer exactamente dos datos.

    CATEGORÍAS VÁLIDAS: FILAMENTOS | IMPRESORAS | ACCESORIOS

    REGLAS DE EXTRACCIÓN:
    - Si el usuario usa pronombres como "esa", "ella", "ese modelo", "el mismo", busca en el historial de conversación el producto real al que se refiere y usa ESE nombre.
    - Si mencionan varios productos, extrae TODOS como palabras clave separadas por coma.
    - Si la intención no es clara, clasifica por el producto más reciente en el historial.
    - Ignora palabras genéricas como "quiero", "tengo", "precio", "cuánto", "hay".

    FORMATO DE RESPUESTA (obligatorio, sin explicaciones, sin texto adicional):
    CATEGORIA: <CATEGORIA> | PALABRAS: <palabra1, palabra2, palabra3>

    Ejemplos correctos:
    CATEGORIA: FILAMENTOS | PALABRAS: PLA, rojo, Bambu
    CATEGORIA: IMPRESORAS | PALABRAS: Creality, Ender 3
    CATEGORIA: ACCESORIOS | PALABRAS: hotend, E3D, compatibilidad'''
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
        columnas_select = ["marca", "modelo", "volumen_impresion", "precio", "stock", "url_imagen"]
    elif "ACCESORIOS" in categoria:
        tabla = "accesorios"
        columnas_busqueda = ["nombre", "compatibilidad"]
        # Columnas específicas de la tabla accesorios
        columnas_select = ["nombre", "compatibilidad", "precio", "stock", "url_imagen"]
    else:
        tabla = "filamentos"
        columnas_busqueda = ["marca", "material", "color"]
        columnas_select = ["marca", "material", "color", "precio", "stock", "url_imagen"]

    # =====================================================================
    # FASE 3: Construcción de la Consulta SQL Dinámica (Buscador Avanzado)
    # =====================================================================
# 1. Limpieza y preparación de palabras clave
    palabras_limpias = palabras_crudas.replace(',', ' ').replace('.', ' ')
    palabras_clave = [p.strip() for p in palabras_limpias.split() if len(p.strip()) > 1]
    
    rango = extraer_rango_precio(mensaje.texto)
    condiciones = []
    parametros = []

    if rango:
        # Caso 1: El usuario pide un rango de precio
        precio_min, precio_max = rango
        condiciones.append("precio BETWEEN ? AND ?")
        parametros.extend([precio_min, precio_max])

    elif palabras_clave:
        # Caso 2: El usuario menciona productos por nombre
        for palabra in palabras_clave:
            sub_condiciones = [f"{col} LIKE ?" for col in columnas_busqueda]
            condiciones.append(f"({' OR '.join(sub_condiciones)})")
            parametros.extend([f"%{palabra}%"] * len(columnas_busqueda))

    query = f"SELECT {', '.join(columnas_select)} FROM {tabla}"

    if condiciones:
        # OR entre condiciones: encuentra cualquier producto que coincida
        query += " WHERE " + " OR ".join(condiciones)

    query += " ORDER BY stock DESC LIMIT 12"

    # =====================================================================
    # EJECUCIÓN EN BASE DE DATOS (Lo que faltaba para definir datos_crudos)
    # =====================================================================
    cursor.execute(query, parametros)
    resultados = cursor.fetchall()

    if resultados:
        # Convertimos las filas de SQL a texto para que el Agente 2 pueda leerlo
        datos_crudos = "\n".join([str(dict(fila)) for fila in resultados])
    else:
        # Si no hay coincidencias, le avisamos al Agente 2
        datos_crudos = "No se encontraron registros en la tabla que coincidan con los criterios."
        
    # (Opcional) Imprimir para monitorear en la terminal qué datos salen de SQLite
    print(f"📦 [Datos SQL Extraídos]: {datos_crudos}")

    # =====================================================================
    # AGENTE 2 (El Evaluador de Stock y Estratega de Ventas)
    # =====================================================================
    
    prompt_agente2_sistema = '''Eres un auditor de inventario para 3Dubble.

    PROCESO OBLIGATORIO:
    1. Lista EXACTAMENTE los productos encontrados con sus datos.
    2. Indica su estado: DISPONIBLE (stock > 0) o SIN STOCK (stock = 0).
    3. Si stock = 0, busca alternativa real en la lista por similitud cromática o técnica.
    4. Si no hay alternativa, indica "Ninguna".

    RESTRICCIONES ABSOLUTAS:
    - NO inventes datos, colores, modelos, precios ni URLs.
    - Copia las URLs de imagen EXACTAMENTE como aparecen, sin modificarlas ni acortarlas.
    - NO uses lenguaje de ventas.
    - SOLO trabaja con los datos recibidos.

    FORMATO DE SALIDA (copia los campos exactamente así):
    PRODUCTO SOLICITADO: [nombre]
    STOCK: [cantidad] → [DISPONIBLE / SIN STOCK]
    PRECIO: [precio]
    IMAGEN: [pega aquí la URL completa tal como está en los datos]
    ALTERNATIVA RECOMENDADA: [nombre o "Ninguna"]
    IMAGEN ALTERNATIVA: [URL completa de la alternativa o "Ninguna"]
    ---'''

    prompt_agente2_usuario = f'''Analiza estos datos de inventario y genera el informe técnico:

    {datos_crudos}

    Pregunta original del cliente: "{mensaje.texto}"
    Determina si el inventario cubre lo que pidió y, si no, identifica la mejor alternativa real de la lista.'''

    respuesta_agente2 = ollama.chat(model='gemma4:latest', messages=[
        {'role': 'system', 'content': prompt_agente2_sistema},
        {'role': 'user',   'content': prompt_agente2_usuario}
    ])
    
    # Ahora los "datos_crudos" que le pasamos al Agente 3 son la evaluación del Agente 2
    datos_analizados_por_agente2 = respuesta_agente2['message']['content']
    print(f"[Agente 2 Resumen]: {datos_analizados_por_agente2}")

    # =====================================================================
    # AGENTE 3 (El Asesor de Ventas Final con contexto total)
    # =====================================================================
    
    mensajes_agente = [
        {
            'role': 'system',
            'content': f'''Eres Duble, el asesor de ventas y soporte técnico de 3Dubble, una tienda especializada en impresión 3D.

    Tu personalidad: experto, directo y genuinamente útil. Hablas de tú al cliente. No suenas como un robot de ventas.

    TIENES ESTOS DATOS DEL INVENTARIO (NO inventes nada que no esté aquí):
    {datos_analizados_por_agente2}

    TU TAREA EN CADA RESPUESTA:
    1. Responde directamente a lo que el cliente preguntó usando SOLO los datos del inventario de arriba.
    2. Si un producto no tiene stock, explícalo con claridad y presenta la alternativa real que aparece en los datos. Di por qué esa alternativa es una buena opción.
    3. SIEMPRE que menciones un producto disponible o una alternativa, MUESTRA su imagen usando Markdown estricto: ![Nombre del Producto](URL_DE_LA_IMAGEN).
    4. Si todos los productos tienen stock, confirma disponibilidad y menciona el precio.
    5. Si EL CLIENTE CONFIRMA LA COMPRA: Genera un ID de pedido único (ej: 3D-8824-X) como confirmación formal.
    6. Si el cliente pide una COTIZACIÓN o TOTAL de varios productos:
   - Suma los precios exactos que aparecen en los datos del inventario.
   - Presenta el desglose línea por línea y el total al final.
   - Formato: Producto → $precio | TOTAL: $suma
   - Si algún producto no aparece en los datos, indícalo explícitamente.
    7. Cierra SIEMPRE con UNA pregunta de validación.

    PROHIBIDO:
    - Inventar precios, colores, modelos o disponibilidad.
    - Inventar URLs de imágenes que no estén en el resumen del inventario.
    - Usar frases genéricas como "¡Excelente elección!" o "¡Con gusto te ayudo!".
    - Repetir la pregunta del cliente textualmente.
    - Terminar con más de una pregunta.'''
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