import ollama

# Usamos el nombre exacto que arrojó la terminal
modelo_usado = 'gemma4:latest' 

print(f"Despertando al agente usando {modelo_usado}...\n")

respuesta = ollama.chat(model=modelo_usado, messages=[
  {
    'role': 'system',
    'content': 'Eres el Agente de Inventario de una tienda de impresión 3D llamada 3Dubble. Responde de forma muy concisa, profesional y con tono de ingeniero.'
  },
  {
    'role': 'user',
    'content': 'Hola, ¿qué tipo de filamento me recomiendas para imprimir engranajes que soporten mucha fricción?'
  }
])

print("🤖 Respuesta del Agente:")
print(respuesta['message']['content'])