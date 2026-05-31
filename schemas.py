from pydantic import BaseModel, Field
from typing import List, Optional

class ElementoPedido(BaseModel):
    producto: str = Field(description="Nombre del producto o refacción solicitada (ej. PLA, Boquilla, Plancha PEI)")
    cantidad: int = Field(default=1, description="Cantidad solicitada de este producto")

class IntencionCliente(BaseModel):
    tipo_solicitud: str = Field(description="Debe ser estrictamente 'COMPRA' si pide productos, o 'SOPORTE' si reporta una falla o duda técnica.")
    productos_solicitados: List[ElementoPedido] = Field(default=[], description="Lista de productos y cantidades extraídos del mensaje. Vacío si es soporte.")
    problema_tecnico: Optional[str] = Field(default=None, description="Descripción breve del problema de impresión 3D detectado. Null si es compra.")
    material_utilizado: Optional[str] = Field(default=None, description="Material mencionado en el problema (ej. PLA, PETG, ABS, ASA). Null si no aplica.")