import streamlit as st
import sqlite3

# --- INICIALIZAR EL CARRITO DE COMPRAS ---
if "carrito" not in st.session_state:
    st.session_state.carrito = []

# --- FUNCIÓN CALLBACK PARA BOTONES ---
def agregar_sustituto_al_carrito(nombre_producto, precio):
    st.session_state.carrito.append({
        "producto": nombre_producto,
        "cantidad": 1,
        "total": precio
    })

# --- BARRA LATERAL (SIEMPRE VISIBLE) --- 
with st.sidebar:
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
            # Opcional: Limpiar el carrito después de comprar
            # st.session_state.carrito = []

# Importamos las clases de tus agentes (eliminamos la línea de consultar_stock que fallaba)
from agente_atencion import AgenteAtencion
from agente_inferencia import AgenteInferencia
from agente_explicador import AgenteExplicador

# Configuración de la página en modo ancho
st.set_page_config(page_title="3Dubble AI", layout="wide", page_icon="🤖")

st.title("🤖 3Dubble: Sistema Multi-Agente para Gestión de Impresión 3D")
st.caption("Orquestación local con Ollama y SQLite para control de insumos y filamentos")

# --- FUNCION PARA CARGAR EL INVENTARIO ---
def cargar_inventario():
    conn = sqlite3.connect("inventario3d.db")
    cursor = conn.cursor()
    # Traemos las nuevas columnas en orden para la tabla de Streamlit
    cursor.execute("SELECT producto_base, tipo, marca, material, color, stock, precio FROM inventario")
    datos = cursor.fetchall()
    conn.close()
    return datos

# --- DISEÑO DE PASARELA EN COLUMNAS ---
col_inv, col_chat = st.columns([1, 2])  # Proporción 1:2 para darle más espacio al chat

# COUMNAP I: Monitor de Inventario Local
with col_inv:
    st.subheader("📦 Inventario de Filamentos")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
    
# Renderizar los datos actualizados de SQLite con mapeo exacto
    inventario = cargar_inventario() # Asegúrate de que tu consulta sea: SELECT producto_base, tipo, marca, material, color, stock, precio FROM inventario
    if inventario:
        import pandas as pd
        # Convertimos a DataFrame y le asignamos los nombres reales de las columnas de la BD
        df_inventario = pd.DataFrame(inventario, columns=[
            "producto_base", "tipo", "marca", "material", "color", "stock", "precio"
        ])
        
        # Ahora configuramos etiquetas bonitas usando los nombres de las columnas
        st.dataframe(df_inventario, column_config={
            "producto_base": "Descripción Base",
            "tipo": "Tipo de Insumo",
            "marca": "Marca",
            "material": "Material",
            "color": "Especificación / Color",
            "stock": "Stock Disponible",
            "precio": "Precio Unitario ($)"
        }, use_container_width=True, hide_index=True)

# COLUMNA II: Consola Multi-Agente y Chat
with col_chat:
    st.subheader("💬 Consola de Control de IA")
    
    # Inicializar el historial del chat en la sesión de Streamlit para que no se borre
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores del historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Entrada de texto del usuario (Chat Input)
    if prompt := st.chat_input("¿Qué deseas imprimir o consultar hoy?"):
        # Mostrar el mensaje del usuario en la pantalla
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Contenedor visual para la respuesta de la IA y el razonamiento de los agentes
        with st.chat_message("assistant"):
            # Creamos los contenedores de las pestañas
            tab1, tab2, tab3, tab_final = st.tabs([
                "🕵️ Agente 1 (Intención)", 
                "🧮 Agente 2 (Inferencia)", 
                "✍️ Agente 3 (Explicación)", 
                "🤖 Respuesta Final"
            ])
            
# --- EJECUCIÓN DEL AGENTE 1 ---
            with tab1:
                st.subheader("Análisis de Lenguaje Natural (Ollama)")
                with st.spinner("Extraendo intenciones..."):
                    
                    # 1. Filtramos y limpiamos el historial (solo peticiones del usuario)
                    mensajes_usuario = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
                    
                    # 2. Juntamos las últimas 2 entradas con un separador limpio
                    historial_limpio = " | ".join(mensajes_usuario[-2:]) if mensajes_usuario else prompt
                    
                    # Inicializamos tu agente de atención
                    atencion = AgenteAtencion()
                    
                    # 🔥 LA CLAVE: Le pasamos el historial limpio al agente
                    intencion_pydantic = atencion.procesar_mensaje(historial_limpio)
                
                st.success("¡Intención extraída con éxito!")
                # Mostramos el JSON estructurado que generó Pydantic
                st.json(intencion_pydantic.model_dump())

            # --- EJECUCIÓN DEL AGENTE 2 ---
            with tab2:
                st.subheader("Motor de Inferencia Determinista (SQLite)")
                with st.spinner("Evaluando reglas de negocio y stock..."):
                    # Inicializamos tu motor experto
                    inferencia = AgenteInferencia()
                    # Pasamos el objeto Pydantic directamente al Agente 2
                    resultado_inferencia = inferencia.procesar_solicitud(intencion_pydantic)
                
                st.success("Cálculo de factibilidad terminado.")
                # Mostramos el diccionario resultante del estado del inventario
                st.write(resultado_inferencia)
                
                if resultado_inferencia.get("aprobado"):
                    for articulo in resultado_inferencia.get("pedido", []):
                        # Verificamos que no esté repetido para no duplicarlo al recargar
                        if articulo not in st.session_state.carrito:
                            st.session_state.carrito.append(articulo)

            # --- ALIMENTAR EL CARRITO (PARCIAL O TOTAL) ---
            # Iteramos sobre los productos que el Agente 2 SÍ logró aprobar (ej. El Amarillo)
            for articulo in resultado_inferencia.get("pedido", []):
                # Validamos que no esté ya en el carrito para no duplicarlo al recargar
                if not any(item["producto"] == articulo["producto"] for item in st.session_state.carrito):
                    st.session_state.carrito.append({
                        "producto": articulo["producto"],
                        "cantidad": articulo["cantidad"],
                        "total": articulo["total"]
                    })
                
            # --- EJECUCIÓN DEL AGENTE 3 ---
            with tab3:
                st.subheader("Generador de Justificaciones (IA Local)")
                with st.spinner("Redactando explicación técnica..."):
                    # Inicializamos tu agente explicador
                    explicador = AgenteExplicador()
                    # Le pasamos el prompt original y el dict del Agente 2
                    argumentacion_final = explicador.explicar_decisiones(prompt, resultado_inferencia)
                
                st.info("Razonamiento del modelo estructurado:")
                st.markdown(argumentacion_final)
       
            # --- PESTAÑA FINAL: EXPERIENCIA DE USUARIO ---
            with tab_final:
                st.subheader("🛍️ Propuesta de Servicio de 3Dubble")
                with st.spinner("Dándole formato comercial al reporte..."):
                    # El prompt que limpia las reglas técnicas para el cliente
                    prompt_consolidacion = f"""
                    Eres el agente de interfaz de 3Dubble. Tu tarea es tomar el siguiente reporte técnico interno de una solicitud de impresión 3D y transformarlo en una respuesta amable, clara y comercial para el cliente final. 
                    Elimina menciones explícitas a código, nombres de variables o reglas lógicas "IF/THEN". Presenta las opciones de forma atractiva.

                    Reporte Técnico:
                    {argumentacion_final}
                    """
                    
                    # Llamada directa a tu Ollama local
                    import ollama
                    response = ollama.generate(model="gemma4", prompt=prompt_consolidacion)
                    respuesta_limpia = response['response']

                st.balloons()  # ¡Efecto de celebración de Streamlit!
                st.markdown(respuesta_limpia)

            # --- INTERFAZ DE BOTONES DINÁMICOS --- 
                if resultado_inferencia.get("estatus") == "REVISIÓN_REABASTECIMIENTO":
                    st.divider()
                    
                    # 1. Base de conocimiento de alternativas (Diccionario Experto)
                    alternativas_db = {
                        "PURPLE": [("LILAC 🟣", "eSUN PLA+ LILAC"), ("MAGENTA 🌺", "eSUN PLA+ MAGENTA")],
                        "RED": [("FIRE ENGINE RED 🚒", "eSUN PLA+ FIRE ENGINE RED"), ("BRICK RED 🧱", "eSUN PLA+ BRICK RED")],
                        "BLUE": [("SOFT BLUE 💧", "eSUN PLA+ SOFT BLUE"), ("SPACE BLUE 🌌", "eSUN PLA+ SPACE BLUE")],
                        "GREEN": [("MINT GREEN 🍃", "eSUN PLA+ MINT GREEN"), ("PINE GREEN 🌲", "eSUN PLA+ PINE GREEN")],
                        "PINK": [("PEACH PINK 🍑", "eSUN PLA+ PEACH PINK"), ("SOFT PINK 🌸", "eSUN PLA+ SOFT PINK")]
                    }
                    
                    # 2. Detector automático del color agotado
                    # Escaneamos el reporte del Agente 2 para ver qué palabra clave activó el fallo
                    color_agotado_encontrado = None
                    inferencias = resultado_inferencia.get("inferencias_realizadas", [])
                    
                    for color_clave in alternativas_db.keys():
                        # Verificamos si la palabra clave (ej. "PURPLE") está en el texto de fallo
                        if any(color_clave in inf for inf in inferencias):
                            color_agotado_encontrado = color_clave
                            break
                            
                    # 3. Renderizado de botones "al vuelo"
                    if color_agotado_encontrado:
                        st.warning("⚠️ Detectamos que un artículo está agotado. ¿Deseas sustituirlo por alguna de estas opciones compatibles?")
                        
                        # Extraemos la lista de opciones para ese color específico
                        opciones = alternativas_db[color_agotado_encontrado]
                        
                        # Creamos la cantidad exacta de columnas según las opciones disponibles
                        cols = st.columns(len(opciones))
                        for i, (label_boton, nombre_producto) in enumerate(opciones):
                            with cols[i]:
                                st.button(
                                    f"Sustituir por {label_boton}", 
                                    key=f"btn_sustituto_{color_agotado_encontrado}_{i}", # Clave única vital en Streamlit
                                    on_click=agregar_sustituto_al_carrito,
                                    args=(nombre_producto, 325.0)
                                )
                    else:
                        st.info("⚠️ Un artículo de tu pedido requiere revisión de stock. Un asesor lo revisará en breve.")
                
        # Guardamos la respuesta verdaderamente consolidada en el historial
        st.session_state.messages.append({"role": "assistant", "content": respuesta_limpia})
