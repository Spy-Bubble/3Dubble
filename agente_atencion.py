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
                "Eres el Agente 1 (Atención al Cliente) de un laboratorio y tienda experta en impresión 3D.\n"
                "Tu objetivo es analizar el mensaje del cliente y extraer con precisión quirúrgica su intención y los datos clave.\n"
                "Clasifica rigurosamente si es COMPRA o SOPORTE técnico.\n"
                "Si el cliente pide filamentos, planchas o refacciones, extrae los nombres y cantidades.\n"
                "Si reporta una falla (ej. problemas de adherencia, atascos, hilos), extrae el problema y el material."
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