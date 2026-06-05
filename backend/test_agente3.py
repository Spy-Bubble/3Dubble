from agente_explicador import AgenteExplicador

# Inicializamos el Agente 3
explicador = AgenteExplicador()

print("==========================================================")
print("🧪 TESTING AGENTE 3: GENERACIÓN DE EXPLICABILIDAD (IA)")
print("==========================================================")

# 1. Simulamos la entrada original del usuario
entrada_original = "Hola, ocupo comprar 2 rollos de Filamento PLA+ Negro 1kg por favor."

# 2. Simulamos el diccionario de resultados que arrojó el Agente 2 (Motor de Inferencia)
resultados_agente2 = {
    "estatus": "PROCESADO",
    "pedido": [
        {
            "id": 1,
            "producto": "Filamento PLA+ Negro 1kg",
            "cantidad": 2,
            "total": 900.0
        }
    ],
    "soluciones": [],
    "inferencias_realizadas": [
        "IF stock de 'Filamento PLA+ Negro 1kg' (5) >= solicitado (2) THEN Pedido Aprobado."
    ]
}

# 3. Ejecutamos el Agente 3 para que nos dé la justificación técnica/comercial
reporte_final = explicador.explicar_decisiones(entrada_original, resultados_agente2)

print("\n--- REPORTE GENERADO POR EL AGENTE 3 ---")
print(reporte_final)
print("==========================================================")