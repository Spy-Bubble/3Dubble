from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class AgenteExplicador:
    def __init__(self):
        self.llm = ChatOllama(model="gemma4", temperature=0.3)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Eres el Agente 3 (Supervisor Técnico) de un sistema experto de impresión 3D.\n"
                "Tu trabajo es comunicar los resultados del Motor de Inferencia (Agente 2) al cliente de forma directa, resumida y al grano.\n\n"
                "REGLAS ESTRICTAS DE FORMATO Y EXPLICABILIDAD:\n"
                "1. VE DIRECTO AL GRANO: Sé conciso, técnico y estructurado. No inventes justificaciones creativas ni divagues.\n"
                "2. EXPLICABILIDAD SINTÉTICA: Menciona brevemente qué regla se activó basándote SOLO en los datos recibidos (ej. 'Pedido aprobado: Stock suficiente', 'Pedido en pausa: Stock de 0 unidades, requiere sustitución').\n"
                "3. ESTRUCTURA DE SALIDA CRÍTICA (¡INQUEBRANTABLE!): NO incluyas saludos largos, notas internas, reflexiones del modelo, ni frases como 'Aquí está la respuesta', 'Como Agente 3 he revisado...' o 'Me encanta este reto'.\n\n"
                "Tu respuesta debe ser ÚNICAMENTE el texto final que leerá el cliente, empezando directamente con el reporte o solución."
            )),
            ("human", (
                "Datos iniciales del cliente: {entrada_cliente}\n"
                "Resultados del Motor de Inferencia: {resultados_inferencia}\n"
                "Genera la respuesta comercial final DIRECTAMENTE sin texto basura:"
            ))
        ])
        self.chain = self.prompt | self.llm

    def explicar_decisiones(self, entrada_original: str, resultados: dict) -> str:
        print("[Agente 3] Generando reporte de explicabilidad y justificación...")
        respuesta = self.chain.invoke({
            "entrada_cliente": entrada_original,
            "resultados_inferencia": str(resultados)
        })
        return respuesta.content