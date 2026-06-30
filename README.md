 # 🤖 Agente IA de Onboarding Corporativo (Multi-Step ReAct)

Trabajo Práctico N° 2 - Inteligencia Artificial (UTN FRSF 2026)  
**Grupo 4**
Mateo Gabriel Blanche - mateoblanche5@gmail.com
José Carlos Cammisi - joseccammisi@gmail.com
Valentino Delarmelina - valentinodelarmelina@outlook.com
Franco Yucci - francoycc@gmail.com

---

## 📌 Descripción del Proyecto
Este repositorio contiene la implementación completa de un **Agente Inteligente Autónomo (Tier 1)** diseñado para actuar como un Mentor de Onboarding para nuevos empleados. 

El sistema abandona el enfoque de un chatbot tradicional para implementar una arquitectura orientada a objetivos mediante un bucle de razonamiento **ReAct (Reasoning and Acting)**. Interactúa con el usuario a través de una **interfaz web nativa (Streamlit)** y cuenta con un sistema de **telemetría en tiempo real (Arize Phoenix)**.

### ✨ Diferenciadores Técnicos Implementados:
1. **RAG Local:** Utiliza `ChromaDB` y modelos de *embeddings* de HuggingFace (`paraphrase-multilingual-MiniLM-L12-v2`) para buscar normativas corporativas sin alucinaciones.
2. **Tools & Function Calling:** Integración nativa con **Google Calendar API**. El agente revisa proactivamente la disponibilidad y agenda reuniones previniendo colisiones (*overlapping*).
3. **Observabilidad:** Servidor local integrado que permite trazar la latencia, los tokens consumidos y las decisiones de ruteo del LLM paso a paso.
4. **Guardrails en Código:** Validaciones estrictas en Python para evitar la sobre-generación de eventos y duplicados.

---

## 🛠️ Stack Tecnológico
* **Orquestador:** LangGraph / LangChain
* **Cerebro (LLM):** `llama-3.3-70b-versatile` (Vía Groq API)
* **Base Vectorial:** ChromaDB
* **Entorno Temporal:** Google Calendar API
* **Interfaz de Usuario:** Streamlit
* **Trazabilidad:** Arize Phoenix

---

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos estrictamente para replicar el entorno y probar el agente sin errores.

### 1. Clonar el repositorio y crear el entorno
\`\`\`bash
git clone https://github.com/francoycc/agente-onboarding-grupo4.git
cd agente-onboarding-grupo4
python -m venv venv

# Activar en Windows: venv\Scripts\activate
# Activar en Mac/Linux: source venv/bin/activate
\`\`\`

### 2. Instalar Dependencias
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Configurar Credenciales
1. Renombra el archivo `.env.example` a `.env` e inserta tu `GROQ_API_KEY`.
2. Asegúrate de colocar tu archivo `credentials.json` (de Google Cloud) en la raíz del proyecto.
3. Asegúrate de que el correo de prueba con el que vas a ingresar esté autorizado en Google Cloud Console.

### 4. Ingesta de Datos (Poblar el RAG)
Antes de interactuar, vectoriza los manuales de la empresa para habilitar la memoria institucional:
\`\`\`bash
python ingest.py
\`\`\`
*(Esto generará la carpeta local `chroma_db/`).*

---

## 💻 Ejecución Dual (Interfaz y Observabilidad)

Para correr la solución completa, deberás utilizar **dos terminales separadas** (ambas con el entorno virtual activado):

**▶️ Consola 1: Iniciar Servidor de Telemetría (Phoenix)**
\`\`\`bash
python -m phoenix.server.main serve
\`\`\`
*(Puedes visualizar la consola de trazabilidad abriendo `http://localhost:6006` en tu navegador).*

**▶️ Consola 2: Iniciar la Interfaz Web del Agente (Streamlit)**
\`\`\`bash
streamlit run app_ui.py --server.fileWatcherType=none
\`\`\`
*(El parámetro `--server.fileWatcherType=none` previene que la aplicación intente monitorear los archivos pesados de HuggingFace en segundo plano. La interfaz se abrirá en `http://localhost:8501`).*

---

## 🧪 Escenario de Prueba Recomendado (Ground Truth)
Para validar la capacidad de ejecución Multi-Step, ingresa el siguiente *prompt* en la interfaz web de Streamlit:

> *"Soy el nuevo desarrollador Junior. Mañana es mi primer día de trabajo. Por favor, buscá en el manual de onboarding qué tareas debo hacer en mi primer día. Luego, revisá si tengo espacio libre mañana por la mañana en mi calendario y, si es así, agendame un bloque de tiempo de 2 horas para hacer esa tarea específica."*

**Comportamiento esperado verificable en la consola Phoenix:**
1. LLM detecta ambigüedad y llama a la Tool `query_company_knowledge`.
2. LLM recupera la duración del curso y llama a `get_calendar_events`.
3. LLM cruza los datos de disponibilidad y ejecuta `insert_calendar_event`.
4. Devuelve el mensaje final en la interfaz web confirmando la reserva.