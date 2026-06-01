import sqlite3
from schemas import IntencionCliente

class AgenteInferencia:
    def __init__(self, db_path='inventario3d.db'):
        self.db_path = db_path

    def consultar_stock(self, nombre_producto: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Busqueda parcial simple en SQL para emparejar el producto
        cursor.execute("SELECT id, producto, stock, precio FROM inventario WHERE producto LIKE ?", (f"%{nombre_producto}%",))
        resultado = cursor.fetchone()
        conn.close()
        return resultado

    def procesar_solicitud(self, datos_cliente: IntencionCliente) -> dict:
        print("[Agente 2] Ejecutando motor de inferencia y reglas de conocimiento...")
        
        reporte_inferencias = []
        pedido_final = []
        soluciones_soporte = []
        estatus_operacion = "PROCESADO"

        # --- MOTOR DE INFERENCIA PARA VENTAS / COMPRAS ---
        if datos_cliente.tipo_solicitud == "COMPRA":
            for item in datos_cliente.productos_solicitados:
                db_item = self.consultar_stock(item.producto)
                
                if db_item:
                    db_id, db_nombre, db_stock, db_precio = db_item
                    
                    # REGLA EXPERTA 1: IF stock >= cantidad THEN aprobar pedido
                    if db_stock >= item.cantidad:
                        total_item = db_precio * item.cantidad
                        pedido_final.append({
                            "id": db_id, "producto": db_nombre, "cantidad": item.cantidad, "total": total_item
                        })
                        reporte_inferencias.append(f"IF stock de '{db_nombre}' ({db_stock}) >= solicitado ({item.cantidad}) THEN Pedido Aprobado.")
                    
                    # REGLA EXPERTA 2: IF stock < cantidad THEN sugerir reabastecimiento o alternativa
                    else:
                        estatus_operacion = "REVISIÓN_REABASTECIMIENTO"
                        reporte_inferencias.append(
                            f"IF stock de '{db_nombre}' ({db_stock}) < solicitado ({item.cantidad}) "
                            f"THEN Sugerir reabastecimiento de urgencia o cambiar por Filamento High-Speed."
                        )
                else:
                    # REGLA EXPERTA 3: IF producto NOT IN inventario THEN rechazar u ofrecer catálogo alterno
                    estatus_operacion = "PRODUCTO_NO_ENCONTRADO"
                    reporte_inferencias.append(f"IF '{item.producto}' no existe en BD THEN Rechazar línea de pedido.")

        # --- MOTOR DE INFERENCIA PARA SOPORTE TÉCNICO (INGENIERÍA DEL CONOCIMIENTO 3D) ---
        elif datos_cliente.tipo_solicitud == "SOPORTE":
            prob = datos_cliente.problema_tecnico.lower() if datos_cliente.problema_tecnico else ""
            mat = datos_cliente.material_utilizado.lower() if datos_cliente.material_utilizado else "pla"

            # REGLA EXPERTA 4: Problemas de adherencia/despegue
            if "despega" in prob or "adherencia" in prob or "cama" in prob:
                if "petg" in mat:
                    soluciones_soporte.append("Aumentar temperatura de la cama a 75°C-80°C. Limpiar con alcohol isopropílico. Usar plancha texturizada de PEI.")
                    reporte_inferencias.append("IF problema == 'despegue' AND material == 'PETG' THEN Inferir ajuste térmico de cama a 80°C y uso de PEI texturizado.")
                else: # Por defecto PLA
                    soluciones_soporte.append("Aumentar temperatura de la cama a 60°C. Calibrar el offset del eje Z (primera capa muy alta).")
                    reporte_inferencias.append("IF problema == 'despegue' AND material == 'PLA' THEN Inferir recalibración de Offset Z y cama a 60°C.")
            
            # REGLA EXPERTA 5: Atascos / Subextrusión
            elif "atasco" in prob or "atascado" in prob or "no sale" in prob:
                soluciones_soporte.append("Realizar método 'Atomic Pull' (tirón en frío). Verificar desgaste de la boquilla de latón de 0.4mm.")
                reporte_inferencias.append("IF problema == 'atasco' THEN Inferir ejecución de Atomic Pull y recomendar reemplazo de Boquilla de Latón.")
            
            else:
                soluciones_soporte.append("Revisar nivelación general de la cama e inspeccionar que el filamento no tenga humedad.")
                reporte_inferencias.append("IF problema desconocido THEN Aplicar regla general de nivelación y secado de filamento.")

        # Retornamos el estado consolidado del sistema experto
        return {
            "estatus": estatus_operacion,
            "pedido": pedido_final,
            "soluciones": soluciones_soporte,
            "inferencias_realizadas": reporte_inferencias
        }