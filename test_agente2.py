from schemas import IntencionCliente, ElementoPedido
from agente_inferencia import AgenteInferencia
import json

# Inicializamos el motor del Agente 2
motor_experto = AgenteInferencia(db_path='inventario3d.db')

print("==========================================================")
print("🧪 CASO A: PROBANDO INFERENCIA DE VENTAS (STOCK VALIDO)")
print("==========================================================")

# Simulamos que el Agente 1 extrajo una solicitud de compra de 2 planchas PEI
datos_compra_ok = IntencionCliente(
    tipo_solicitud="COMPRA",
    productos_solicitados=[
        ElementoPedido(producto="Plancha de PEI Texturizado", cantidad=2)
    ]
)

resultado_compra = motor_experto.procesar_solicitud(datos_compra_ok)
print(json.dumps(resultado_compra, indent=2, ensure_ascii=False))


print("\n==========================================================")
print("🧪 CASO B: PROBANDO INFERENCIA DE SOPORTE (REGLA PETG)")
print("==========================================================")

# Simulamos que el Agente 1 detectó un problema de despegue usando material PETG
datos_soporte_petg = IntencionCliente(
    tipo_solicitud="SOPORTE",
    problema_tecnico="se despega de la cama",
    material_utilizado="PETG"
)

resultado_soporte = motor_experto.procesar_solicitud(datos_soporte_petg)
print(json.dumps(resultado_soporte, indent=2, ensure_ascii=False))