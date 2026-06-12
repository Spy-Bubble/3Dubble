import sqlite3
import ollama

# 1. Función para buscar en tu base de datos
def consultar_stock(material_buscado):
    conexion = sqlite3.connect('backend/inventario3d.db')
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    # Buscamos filamentos que coincidan con lo que pide el cliente
    cursor.execute("SELECT marca, material, color, precio, stock FROM filamentos WHERE material LIKE ?", (f'%{material_buscado}%',))
    resultados = cursor.fetchall()
    conexion.close()
    
    # Formateamos los datos como un texto crudo
    if not resultados:
        return "No hay resultados en la base de datos."
    
    texto_datos = "DATOS DE LA BASE DE DATOS:\n"
    for fila in resultados:
        texto_datos += f"- {fila['marca']} {fila['material']} ({fila['color']}) | Precio: ${fila['precio']} | Stock: {fila['stock']}\n"
    
    return texto_datos

# 2. Simulamos la consulta de un cliente
pregunta_cliente = "¿Qué colores tienes disponibles en PLA+ y cuánto cuestan?"
datos_crudos = consultar_stock("PLA+")

print("🔍 Datos extraídos por Python de SQLite:")
print(datos_crudos)
print("-" * 40)

# 3. Le pasamos el contexto al Agente
print("🤖 Generando respuesta del agente...\n")
respuesta = ollama.chat(model='gemma4:latest', messages=[
  {
    'role': 'system',
    'content': f'''Eres el Agente de Soporte y Ventas de 3Dubble. 
    Usa EXCLUSIVAMENTE los siguientes datos de inventario para responder al cliente. 
    No inventes productos ni precios. Sé amable, persuasivo y conciso.
    
    {datos_crudos}'''
  },
  {
    'role': 'user',
    'content': pregunta_cliente
  }
])

print("💬 Respuesta final para el cliente:")
print(respuesta['message']['content'])