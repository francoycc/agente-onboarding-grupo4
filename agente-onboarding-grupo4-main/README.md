 AGENTE IA DE ONBOARDING CORPORATIVO (MULTI-STEP REACT)
========================================================================
Trabajo Práctico N° 2 - Inteligencia Artificial (UTN FRSF 2026)
Grupo Nro 4
Materia: Inteligencia Artificial

Integrantes:
- Mateo Gabriel Blanche (mateoblanche5@gmail.com)
- José Carlos Cammisi (joseccammisi@gmail.com)
- Valentino Delarmelina (valentinodelarmelina@outlook.com)
- Franco Yucci (francoycc@gmail.com)

------------------------------------------------------------------------
 1. DESCRIPCIÓN DEL PROYECTO
------------------------------------------------------------------------
Este repositorio contiene la implementación completa y real de un Agente Inteligente Autónomo (Tier 1) encargado de asistir en el proceso de inducción (onboarding) y mentoría para nuevos empleados dentro de una organización. 

El sistema rompe con el paradigma de los chatbots tradicionales al utilizar un bucle iterativo de planificación y ejecución basado en el framework ReAct (Reasoning and Acting) sobre grafos de estado. El agente procesa intenciones ambiguas en lenguaje natural, recupera políticas y guías de estudio utilizando un módulo RAG (Retrieval-Augmented Generation) y modifica de manera determinística el entorno digital a través de la API de Google Calendar, garantizando la ausencia de conflictos horarios (overlapping).

 Diferenciadores Técnicos Core:
- Arquitectura ReAct Multi-Step: Implementada de forma explícita mediante LangGraph, controlando de manera fina las transiciones entre nodos de pensamiento ("agent") y nodos de acción ("tools").
- Módulo RAG Local 100% Gratuito: Integración nativa con ChromaDB y embeddings vectoriales de HuggingFace ("all-MiniLM-L6-v2") corriendo de manera local sin necesidad de costos en API externas.
- Razonamiento de Ultra-Baja Latencia: Inferencia orquestada con Llama 3.3 (llama-3.3-70b-versatile) corriendo de manera gratuita en los servidores distribuidos de Groq Cloud.
- Guardrails e Idempotencia: Bloqueo algorítmico a nivel de Tool en Python para prevenir que el LLM genere por duplicado o triplicado eventos superpuestos en un mismo turno conversacional.
- Memoria Conversacional Multi-Turno: Reductor de estados en LangGraph (MessagesState) para resolver de forma fluida referencias anafóricas y negociaciones de horarios.

------------------------------------------------------------------------
 2. ESTRUCTURA COMPLETA DEL REPOSITORIO
------------------------------------------------------------------------
Asegúrese de que el espacio de trabajo en su editor (VS Code) respete la siguiente arquitectura modular para el correcto mapeo de paquetes:

agente-onboarding-grupo4/
│
├── data/
│   └── manual_onboarding.txt   <-- Corpus documental (Políticas de inducción y Learning Paths)
│
├── src/
│   ├── __init__.py             <-- Obligatorio para inicializar el módulo src
│   ├── core/
│   │   ├── __init__.py
│   │   └── agent.py            <-- Definición del grafo de LangGraph, System Prompt y ChatGroq
│   │
│   └── tools/
│       ├── __init__.py
│       ├── calendar_tools.py   <-- Endpoints de Google Calendar API (Lectura/Escritura/Duplicados)
│       └── rag_tools.py        <-- Conector semántico de consulta a ChromaDB y HuggingFace
│
├── .env                        <-- Variables de entorno locales (Groq API Key)
├── .env.example                <-- Plantilla limpia de variables para el repositorio de GitHub
├── .gitignore                  <-- Configurado para evitar fugas de secretos (Ignora .env, tokens, chroma_db)
├── credentials.json            <-- Credenciales OAuth de la Consola de Google Cloud
├── ingest.py                   <-- Script para la segmentación, embedding e indexación de la base RAG
├── main.py                     <-- Interfaz de usuario por consola y loop de persistencia de eventos
└── requirements.txt            <-- Lista de dependencias del entorno virtual congeladas (pip freeze)

------------------------------------------------------------------------
 3. REQUISITOS PREVIOS Y CONFIGURACIÓN DEL ENTORNO
------------------------------------------------------------------------

Paso 3.1: Clonar el Repositorio e Inicializar
> git clone https://github.com/francoycc/agente-onboarding-grupo4.git
> cd agente-onboarding-grupo4

Paso 3.2: Crear y Activar el Entorno Virtual (Aislamiento de Módulos)
- En Windows (PowerShell / CMD):
  > python -m venv venv
  > .\venv\Scripts\activate
- En Mac / Linux:
  > python -m venv venv
  > source venv/bin/activate

Al activarlo, verá el prefijo '(venv)' en su terminal.

Paso 3.3: Instalar Dependencias Congeladas
Con el entorno virtual activado, instale los paquetes requeridos por la cátedra y las integraciones oficiales:
> pip install -r requirements.txt

Paso 3.4: Configuración de Variables de Entorno (.env)
1. Copie el archivo de ejemplo:
   > cp .env.example .env (o renómbrelo manualmente a .env)
2. Abra el archivo `.env` en VS Code y configure su clave de Groq:
   GROQ_API_KEY=gsk_coloque_aqui_su_clave_real_de_groq

Paso 3.5: Configuración de Credenciales de Google Calendar API
1. El archivo `credentials.json` (obtenido al registrar una Desktop Application en Google Cloud Console) debe ubicarse obligatoriamente en la raíz del proyecto.
2. Asegúrese de haber agregado su cuenta de correo personal de Gmail (ej. francoycc@gmail.com) dentro de la sección "Test Users" (Usuarios de prueba) de la Pantalla de Consentimiento de OAuth de su consola de Google.

------------------------------------------------------------------------
 4. EJECUCIÓN DEL AGENTE Y PIPELINE DE INGESTA
------------------------------------------------------------------------

Fase A: Ingesta e Indexación de Datos (Poblar ChromaDB)
Antes de interactuar, es necesario vectorizar los manuales de la empresa. Coloque la información de texto dentro de `data/manual_onboarding.txt` y ejecute:
> python ingest.py

Verá cómo se descarga localmente el modelo de oraciones de HuggingFace, segmenta el documento y crea de manera persistente la carpeta `chroma_db/`.

Fase B: Ejecución del Agente e Interacción
Inicie el bucle cognitivo transaccional del agente ejecutando:
> python main.py

⚠️ NOTA IMPORTANTE EN LA PRIMERA INTERACCIÓN:
La primera vez que el agente requiera inspeccionar o escribir en su agenda, el script de Python abrirá automáticamente una pestaña en su navegador web predeterminado. 
1. Inicie sesión con la cuenta de Gmail autorizada en la consola de Google.
2. Si aparece el cartel "Google no verificó esta app", haga clic en "Configuración Avanzada" y luego en el enlace "Ir a agente-onboarding-grupo4 (no seguro)".
3. Conceda todos los permisos solicitados de lectura y escritura de calendarios.
4. Tras confirmarse el éxito en el navegador, se creará el archivo local `token.json`. A partir de allí, el agente funcionará de manera silenciosa en segundo plano por consola.

------------------------------------------------------------------------
 5. ESCENARIO DE PRUEBA DE EVALUACIÓN
------------------------------------------------------------------------
Para validar el comportamiento y el funcionamiento cruzado de RAG + Tools sin alucinaciones ni duplicaciones, ingrese el siguiente prompt exacto en el prompt de comandos:

"Soy el nuevo desarrollador Junior. Mañana es mi primer día de trabajo. Por favor, buscá en el manual de onboarding qué tareas debo hacer en mi primer día. Luego, revisá si tengo espacio libre mañana por la mañana en mi calendario y, si es así, agendame un bloque de tiempo de 2 horas para hacer esa tarea específica."

🔍 TRAZABILIDAD ESPERADA EN CONSOLA (LOGGING DE OBSERVABILIDAD):
- El agente inicia el procesamiento en el nodo `agent` evaluando el System Prompt.
- Detecta que no posee el conocimiento sobre las tareas y emite un Tool Call para `query_company_knowledge`.
- El nodo de herramientas ejecuta el RAG en ChromaDB y devuelve el texto con el Curso Obligatorio de Git de 2 horas de duración.
- El flujo retorna al nodo `agent` de forma cíclica. El modelo razona que ahora necesita buscar disponibilidad y emite un Tool Call para `get_calendar_events` mapeando las marcas de tiempo ISO 8601 del día de mañana.
- Al verificar que no hay colisiones horarias (no hay overlapping duro), el agente invoca de manera autónoma la herramienta `insert_calendar_event` parametrizando el título, descripción y horarios idóneos.
- La herramienta física de Python intercepta la solicitud, realiza la validación de duplicados y efectúa el POST seguro a los servidores de Google Cloud.
- Finalmente, el modelo concluye el plan de pasos lógicos y emite una respuesta sintetizada en lenguaje natural amigable indicando el link del evento real generado.

========================================
Grupo4 - 2026
========================================
