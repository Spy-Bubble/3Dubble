from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from schemas import IntencionCliente

class AgenteAtencion:
    def __init__(self):
        # Configuramos el modelo local gemma4 a través de Ollama
        # Fijamos la temperatura en 0 para que sea preciso y no invente datos
        self.llm = ChatOllama(model="gemma4", temperature=0.0)
        # Forzamos al LLM a que devuelva su respuesta estructurada según nuestro esquema Pydantic
        self.structured_llm = self.llm.with_structured_output(IntencionCliente)
        
        # Diseñamos el prompt del sistema para entrenar al Agente 1
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
"""
                Eres el Agente 1 de 3Dubble. Tu objetivo es normalizar el lenguaje natural del cliente hacia las claves de fábrica de nuestro catálogo de filamentos. 

                REGLAS ESTRICTAS DE EXTRACCIÓN (JSON/PYDANTIC) - ¡INQUEBRANTABLES!:
                1. TIPO DE SOLICITUD: El campo 'tipo_solicitud' DEBE ser estrictamente "COMPRA" o "SOPORTE". Está PROHIBIDO usar cualquier otro término (como "Consulta", "Cotización" o "Stock").
                2. PRODUCTOS: NUNCA dejes la lista 'productos_solicitados' vacía si el cliente menciona un color, material o intención de pedido.
                3. FORMATO EXACTO: En el campo 'producto' NUNCA pongas descripciones en español (ej. "Filamento morado" o "Rollo amarillo"). Pon ÚNICAMENTE la clave exacta que resulte de la matriz de equivalencias de abajo.

                Para interpretar los colores y sus variantes, aplica estrictamente este sistema de relación semántica basado en dos dimensiones:

                1. DIMENSIÓN: COLORES BASE
                Asocia las palabras del cliente a una raíz estándar:
                - "Rosa" / "Rosado" -> Raíz: PINK
                - "Azul" -> Raíz: BLUE
                - "Verde" -> Raíz: GREEN
                - "Rojo" / "Colorado" -> Raíz: RED
                - "Morado" / "Púrpura" / "Lila" -> Raíz: PURPLE
                - "Amarillo" / "Canario" / "Mostaza" -> Raíz: YELLOW
                - "Blanco" -> Raíz: WHITE
                - "Naranja" -> Raíz: ORANGE

                2. DIMENSIÓN: TONALIDADES / MODIFICADORES
                Identifica si el usuario aplica un adjetivo calificativo para ajustar la raíz del color:
                - Variantes Claras / Pasteles ("bajito", "pastel", "clarito", "mostaza" o diminutivos como "rosita"): 
                    Asocia el prefijo o modificador "SOFT", "LIGHT" o "ALMOND".
                - Variantes Intensas / Fuertes ("fuerte", "rey", "bandera", "canario", "vivo"): 
                    Asocia el prefijo o modificador "RGB", "DARK" o el nombre puro del color.

                3. MATRIZ DE EQUIVALENCIAS OFICIALES (Catálogo eSUN):
                Usa las dos dimensiones anteriores para mapear hacia el catálogo real de la base de datos:
                - Raíz PURPLE -> "PLA+-PURPLE"
                - Raíz YELLOW + Estándar/Fuerte/Canario -> "YELLOW"
                - Raíz YELLOW + Modificador Pastel/Mostaza -> "ALMOND YELLOW"
                - Raíz PINK + Modificador Pastel/Bajito -> "SOFT PINK"
                - Raíz PINK + Estándar/Fuerte -> "PLA+-PINK"
                - Raíz BLUE + Modificador Fuerte/Rey -> "RGB BLUE"
                - Raíz BLUE + Modificador Pastel/Bajito -> "SOFT BLUE"
                - Raíz GREEN + Modificador Fuerte -> "RGB GREEN"
                - Raíz GREEN + Modificador Pastel/Menta -> "MINT GREEN"
                - Raíz WHITE + Estándar/Leche -> "MILKY WHITE"

                4. REGLAS DE SUSTITUCIÓN Y SIMILITUD CROMÁTICA:
                Si el cliente pregunta por un color "similar", "parecido", o un "sustituto" para un color que no hay, DEBES aplicar estas deducciones lógicas basadas en la familia de colores y extraer la alternativa en el JSON:
                - Similar / Sustituto de Morado o Púrpura -> Extrae "LILAC" o "MAGENTA".
                - Similar / Sustituto de Rosa -> Extrae "PEACH PINK" o "SOFT PINK".
                - Similar / Sustituto de Azul -> Extrae "SOFT BLUE" o "HAZE BLUE".
                - Similar / Sustituto de Verde -> Extrae "MINT GREEN" o "PINE GREEN".

                REGLA DE CONTEXTO ESTRICTA: Si el cliente SOLO está pidiendo un sustituto para un color específico (ej. "¿qué color similar al morado tienen?"), EXTRAE ÚNICAMENTE el producto sustituto (ej. "LILAC"). NO vuelvas a incluir los otros colores de mensajes anteriores a menos que el cliente explícitamente diga que los agregues al carrito.

                REGLA DE ADAPTACIÓN EN LENGUAJE NATURAL:
                Si el cliente utiliza un diminutivo o adjetivo que denote tonalidad (ej. "amarillito bajito", "verdecito pastel"), aunque no esté explícitamente en la lista de arriba, deduce por lógica conceptual que busca la versión "SOFT", "LIGHT" o la raíz directa en inglés de ese material.
                """
            )),
            ("human", "{mensaje_usuario}")
        ])
        
        # Creamos la cadena de ejecución (Chain)
        self.chain = self.prompt | self.structured_llm

    def procesar_mensaje(self, mensaje: str) -> IntencionCliente:
        try:
            print("[Agente 1] Analizando la intención del cliente...")
            resultado = self.chain.invoke({"mensaje_usuario": mensaje})
            return resultado
        except Exception as e:
            print(f"[Agente 1] Error al procesar con el LLM: {e}")
            # Retorno seguro en caso de fallo de parsing
            return IntencionCliente(tipo_solicitud="SOPORTE", problema_tecnico="Error de procesamiento local")

# Pequeña prueba local del Agente 1
if __name__ == "__main__":
    agente = AgenteAtencion()
    
    # Caso de prueba 2: Soporte Técnico
    test_soporte = "Hola, mi impresora está sacando muchos hilos parecidos a telarañas cuando uso filamento PETG."
    res_soporte = agente.procesar_mensaje(test_soporte)
    print("\n--- Resultado Extraído (Soporte) ---")
    print(res_soporte.model_dump_json(indent=2))