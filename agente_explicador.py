from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class AgenteExplicador:
    def __init__(self):
        self.llm = ChatOllama(model="gemma4", temperature=0.3)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Eres el Agente 3 (Supervisor y Explicador Técnico) de un sistema experto de impresión 3D.\n"
                "Tu trabajo es revisar las acciones tomadas por el Motor de Inferencia (Agente 2) y redactar una respuesta final impecable, clara y transparente para el usuario.\n"
                "DEBES CUMPLIR CON LA EXPLICABILIDAD: Explica de forma explícita al cliente qué inferencias/reglas del sistema experto se activaron y por qué (ej. disponibilidad de stock, parámetros térmicos del material).\n"
                "Mantén un tono profesional, ingenieril y amable."
            )),
            ("human", (
                "Datos iniciales del cliente: {entrada_cliente}\n"
                "Resultados del Motor de Inferencia: {resultados_inferencia}\n"
                "Genera el reporte de explicabilidad y respuesta final:"
            ))
        ])
        self.chain = self.prompt | self.llm

    # 🔍 REVISA ESTA LÍNEA: Debe tener 4 espacios de sangría y llamarse exactamente así:
    def explicar_decisiones(self, entrada_original: str, resultados: dict) -> str:
        print("[Agente 3] Generando reporte de explicabilidad y justificación...")
        respuesta = self.chain.invoke({
            "entrada_cliente": entrada_original,
            "resultados_inferencia": str(resultados)
        })
        return respuesta.content