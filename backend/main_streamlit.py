import streamlit as st
import sqlite3
# Importa tus agentes y utilidades aquí...
from agente_atencion import AgenteAtencion
from agente_inferencia import AgenteInferencia
from agente_explicador import AgenteExplicador
from schemas import IntencionCliente, ElementoPedido

st.set_page_config(page_title="3Dubble Sistema Experto", page_icon="🧊", layout="wide")

# --- FUNCIÓN AUXILIAR PARA BASE DE DATOS ---
def asegurar_esquema_db():
    """Verifica si la base de datos tiene la nueva estructura y la actualiza si no es así."""
    conn = sqlite3.connect("inventario3d.db")
    cursor = conn.cursor()
    try:
        # Intentamos leer la nueva columna
        cursor.execute("SELECT tipo_insumo FROM inventario LIMIT 1")
    except sqlite3.OperationalError:
        # Si da error, significa que no existe. ¡La creamos en este instante!
        cursor.execute("ALTER TABLE inventario ADD COLUMN tipo_insumo TEXT DEFAULT 'Filamento'")
        conn.commit()
    finally:
        conn.close()

# Ejecutamos el chequeo silencioso cada vez que arranca la app
asegurar_esquema_db()

def consultar_opciones(query, parametros=()):
    conn = sqlite3.connect("inventario3d.db")
    cursor = conn.cursor()
    cursor.execute(query, parametros)
    resultados = [fila[0] for fila in cursor.fetchall()]
    conn.close()
    return resultados

# ==========================================
# 1. INICIALIZACIÓN DE MEMORIA Y CARRITO
# ==========================================
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "messages_soporte" not in st.session_state:
    st.session_state.messages_soporte = [] # Historial separado solo para soporte

# ==========================================
# 2. BARRA LATERAL (NAVEGACIÓN Y CARRITO)
# ==========================================
with st.sidebar:
    st.title("⚙️ 3Dubble OS")
    
    # Menú de navegación principal
    modulo_activo = st.radio(
        "Selecciona el Módulo Operativo:",
        ["🛒 Compras e Inventario", "🛠️ Soporte Técnico (IA)"]
    )
    
    st.divider()
    
    # El carrito siempre visible
    st.header("🛒 Tu Pedido Actual")
    if len(st.session_state.carrito) == 0:
        st.info("Tu carrito está vacío.")
    else:
        total_pagar = 0
        for i, item in enumerate(st.session_state.carrito):
            st.markdown(f"**{item['cantidad']}x {item['producto']}** - ${item['total']}")
            total_pagar += item['total']
        
        st.divider()
        st.subheader(f"Total: ${total_pagar}")
        if st.button("Finalizar Compra ✅"):
            st.balloons()
            st.success("¡Pedido enviado a producción!")
            st.session_state.carrito = [] # Limpiamos tras comprar
            st.rerun()

# ==========================================
# 3. MÓDULO 1: COMPRAS (FILTROS INDEPENDIENTES)
# ==========================================
if modulo_activo == "🛒 Compras e Inventario":
    
    # 🔥 1. Variables inicializadas en la raíz para silenciar a Pylint
    btn_analizar = False
    cantidad_final = 1
    producto_elegido_str = ""

    st.header("📦 Catálogo Dinámico de 3Dubble")
    st.write("Filtra los productos como prefieras. ¡No hay un orden obligatorio!")
    
    # --- SECCIÓN 1: FILTROS INDEPENDIENTES ---
    st.subheader("🔍 Filtros de Búsqueda")
    
    # Colocamos los 4 filtros en línea horizontal para ahorrar espacio
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        tipos_db = consultar_opciones("SELECT DISTINCT tipo FROM inventario")
        tipo_sel = st.selectbox("Categoría:", ["--- Todos ---"] + (tipos_db if tipos_db else []))
        
    with col_f2:
        marcas_db = consultar_opciones("SELECT DISTINCT marca FROM inventario")
        marca_sel = st.selectbox("Marca:", ["--- Todos ---"] + (marcas_db if marcas_db else []))
        
    with col_f3:
        mat_db = consultar_opciones("SELECT DISTINCT material FROM inventario")
        mat_sel = st.selectbox("Familia/Material:", ["--- Todos ---"] + (mat_db if mat_db else []))
        
    with col_f4:
        color_db = consultar_opciones("SELECT DISTINCT color FROM inventario")
        color_sel = st.selectbox("Variante/Color:", ["--- Todos ---"] + (color_db if color_db else []))

    # --- SECCIÓN 2: MOTOR DE BÚSQUEDA DINÁMICO ---
    # Armamos la consulta SQL sumando solo los filtros que el usuario haya seleccionado
    query_base = "SELECT tipo, marca, material, color, precio, stock, url_imagen FROM inventario WHERE 1=1"
    parametros = []
    
    if tipo_sel != "--- Todos ---":
        query_base += " AND tipo = ?"
        parametros.append(tipo_sel)
    if marca_sel != "--- Todos ---":
        query_base += " AND marca = ?"
        parametros.append(marca_sel)
    if mat_sel != "--- Todos ---":
        query_base += " AND material = ?"
        parametros.append(mat_sel)
    if color_sel != "--- Todos ---":
        query_base += " AND color = ?"
        parametros.append(color_sel)
        
    # Ejecutamos la búsqueda con las condiciones armadas
    conn = sqlite3.connect("inventario3d.db")
    cursor = conn.cursor()
    cursor.execute(query_base, parametros)
    productos_encontrados = cursor.fetchall()
    conn.close()
    
    st.divider()

    # --- SECCIÓN 3: RESULTADOS Y COMPRA ---
    if not productos_encontrados:
        st.warning("⚠️ No encontramos ningún producto con esa combinación exacta de filtros.")
    else:
        st.success(f"✅ Se encontraron {len(productos_encontrados)} producto(s) coincidentes.")
        
        # Formateamos la lista de resultados para mostrarlos en un menú final
        # Cada fila trae: (tipo, marca, material, color, precio, stock, url_imagen)
        lista_nombres = [f"{p[0]} {p[1]} {p[2]} {p[3]}" for p in productos_encontrados]
        
        col_res, col_img = st.columns([2, 1])
        
        with col_res:
            producto_elegido_str = st.selectbox("👇 Selecciona el producto exacto a visualizar/comprar:", lista_nombres)
            
            # Obtenemos todos los datos del producto seleccionado
            idx = lista_nombres.index(producto_elegido_str)
            prod_data = productos_encontrados[idx]
            stock_disponible = prod_data[5]
            
            st.markdown(f"**Precio:** ${prod_data[4]:,.2f}")
            st.markdown(f"**Stock Disponible:** {stock_disponible} unidades")
            
            if stock_disponible > 0:
                cantidad_final = st.number_input("Cantidad deseada:", min_value=1, max_value=stock_disponible, value=1)
                btn_analizar = st.button("🛍️ Analizar y Agregar al Carrito", type="primary")
            else:
                st.error("⚠️ Este producto está agotado actualmente (Stock 0).")
                
        with col_img:
            url_img = prod_data[6]
            if url_img:
                st.image(url_img, use_container_width=True)
            else:
                st.info("🖼️ Imagen no disponible")

    # --- SECCIÓN 4: LÓGICA DE MOTOR DE INFERENCIA ---
    if btn_analizar:
        with st.spinner("Motor de inferencia validando stock..."):
            
            datos_compra = IntencionCliente(
                tipo_solicitud="COMPRA",
                productos_solicitados=[ElementoPedido(producto=producto_elegido_str, cantidad=locals().get("cantidad_seleccionada", 1))]
            )
            
            agente_inferencia = AgenteInferencia()
            resultado = agente_inferencia.procesar_solicitud(datos_compra)
            
            if resultado.get("aprobado"):
                for articulo in resultado.get("pedido", []):
                    # Validar para no duplicar en UI
                    if not any(item["producto"] == articulo["producto"] for item in st.session_state.carrito):
                        st.session_state.carrito.append({
                            "producto": articulo["producto"],
                            "cantidad": articulo["cantidad"],
                            "total": articulo["total"]
                        })
                st.success(f"¡{cantidad_final}x {producto_elegido_str} agregado con éxito!")
                st.rerun()
            else:
                st.error("⚠️ El sistema ha detectado una inconsistencia de stock.")
                agente3 = AgenteExplicador()
                explicacion = agente3.explicar_decisiones("Explicación de inventario", resultado)
                st.markdown(explicacion)
# ==========================================
# 4. MÓDULO 2: SOPORTE TÉCNICO (IA CONVERSACIONAL)
# ==========================================
elif modulo_activo == "🛠️ Soporte Técnico (IA)":
    st.header("🤖 Asistente Experto de Impresión 3D")
    st.write("¿Tienes problemas de adherencia, atascos o dudas de temperaturas? Describe tu problema:")
    
    # Dibujar el historial de chat de soporte
    for message in st.session_state.messages_soporte:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input de lenguaje natural (Aquí sí usamos al Agente 1)
    if prompt := st.chat_input("Ej: Mi pieza de PETG se despega de la cama..."):
        st.session_state.messages_soporte.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Analizando con ingeniería de conocimiento..."):
                pass