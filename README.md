# 3Dubble: Plataforma E-Commerce y Sistema Soporte Multi-Agente IA

Plataforma integral de comercio electrónico especializada en impresión 3D (filamentos, impresoras y accesorios). Este proyecto destaca por la implementación de un **Sistema Multi-Agente RAG local**, que funciona como un asistente de ventas inteligente capaz de consultar bases de datos en tiempo real y guiar a los clientes de forma conversacional.

## Stack Tecnológico
* **Frontend:** React.js, Tailwind CSS, React Router DOM, React Markdown.
* **Backend:** Python, FastAPI, SQLite3.
* **Inteligencia Artificial:** Ollama (Modelo local `gemma4:latest`), Arquitectura RAG (Retrieval-Augmented Generation).

## Requisitos del Sistema (Hardware y Software)
Para ejecutar este proyecto, especialmente el motor de inteligencia artificial local, se requiere:
* Python 3.10+ y Node.js instalados.
* [Ollama](https://ollama.com/) instalado en el sistema.
* **Hardware:** Para una inferencia fluida sin latencia perceptible en el agente de ventas, se recomienda una GPU dedicada con buena capacidad de VRAM, para este proyecto se uso una NVIDIA GeForce RTX 4060 Ti.

--- 

## Instrucciones Básicas de Instalación y Ejecución

Sigue estos pasos para levantar el entorno de desarrollo local:

### 1. Preparar el Cerebro de IA (Ollama)
Abre una terminal y descarga el modelo necesario para los agentes. Mantén la aplicación ejecutándose en segundo plano:

```bash
ollama run gemma4:latest
```

### 2. Levantar el Backend (FastAPI + SQLite)
Abre una terminal en la raíz del proyecto y ejecuta:

```bash
# Instalar dependencias de Python
pip install fastapi uvicorn pydantic ollama sqlite3

# Inicializar la base de datos (crear archivo inventario3d.db desde cero)
python backend/init_db.py

# Iniciar el servidor (escuchando en http://localhost:8000)
uvicorn backend.main:app --reload
```

### 3. Levantar el Frontend (React)
Abre una nueva terminal, navega a la carpeta del frontend y ejecuta:

```bash
cd frontend

# Instalar dependencias de Node
npm install

# Iniciar el servidor de desarrollo
npm run dev
```

### 4. Uso de la Plataforma
1. Abre tu navegador en la dirección que indique Vite (generalmente `http://localhost:5173`).
2. Navega por las secciones de la tienda (Impresoras, Filamentos, Accesorios).
3. Abre el menú desplegable y selecciona **Soporte IA** para interactuar con el sistema multi-agente, el cual consultará dinámicamente el inventario de SQLite para responder a tus dudas.

### 5. Estructura Principal
* **`/backend`**: Contiene la lógica del servidor (FastAPI), la base de datos (SQLite) y el enrutamiento de los agentes IA.
* **`/frontend`**: Contiene los componentes visuales de React, el diseño en Tailwind y la interfaz gráfica del chat.
