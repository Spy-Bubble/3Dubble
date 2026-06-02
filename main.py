import streamlit as st
import sqlite3

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
    
    # Renderizar los datos de SQLite en una tabla interactiva nativa
    inventario = cargar_inventario()
    if inventario:
        st.dataframe(inventario, column_config={
            "0": "Material / Producto",
            "1": "Tipo de Insumo",
            "2": "Stock Disponible",
            "3": "Precio Unitario ($)"
        }, use_container_width=True)
    else:
        st.warning("La base de datos está vacía o no se ha inicializado.")

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
                with st.spinner("Extraiendo intenciones..."):
                    # Inicializamos tu agente de atención
                    atencion = AgenteAtencion()
                    # Procesamos el mensaje para obtener el objeto Pydantic
                    intencion_pydantic = atencion.procesar_mensaje(prompt)
                
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
                
        # Guardamos la respuesta verdaderamente consolidada en el historial
        st.session_state.messages.append({"role": "assistant", "content": respuesta_limpia})
                
        # Guardamos la respuesta del asistente en el historial para la persistencia
        st.session_state.messages.append({"role": "assistant", "content": argumentacion_final})