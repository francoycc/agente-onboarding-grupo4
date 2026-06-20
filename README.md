# Agente de Onboarding y Mentoría (Grupo 4)

Trabajo Práctico N° 2 - Inteligencia Artificial (UTN FRSF 2026)

## Descripción
Este repositorio contiene el código fuente de un Agente Inteligente Autónomo basado en LLM (Tier 1) diseñado para asistir en el proceso de inducción de nuevos empleados. Implementa un bucle **ReAct multi-step** orquestado con LangGraph.

El agente utiliza **RAG (Retrieval-Augmented Generation)** para consultar manuales corporativos y planes de estudio, y se conecta vía **API a Google Calendar** para gestionar proactivamente los bloques de capacitación sin generar superposiciones horarias.

## Tecnologías y Dependencias
- **Orquestación:** LangGraph / LangChain
- **LLM:** OpenAI `gpt-4o-mini`
- **Base de Datos Vectorial (RAG):** ChromaDB
- **Integraciones:** Google Calendar API

## Instalación y Ejecución

### 1. Clonar el repositorio
\`\`\`bash
git clone https://github.com/usuario/agente-onboarding-grupo4.git
cd agente-onboarding-grupo4
\`\`\`

### 2. Configurar el Entorno Virtual
\`\`\`bash
python -m venv venv
# Activar (Windows): venv\Scripts\activate
# Activar (Mac/Linux): source venv/bin/activate
\`\`\`

### 3. Instalar Dependencias
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Configurar Credenciales
1. Renombrar el archivo `.env.example` a `.env` y colocar su `OPENAI_API_KEY`.
2. Colocar el archivo `credentials.json` (de Google Cloud Console) en la raíz del proyecto para habilitar la API de Calendar.

### 5. Ejecutar el Agente
\`\`\`bash
python main.py
\`\`\`