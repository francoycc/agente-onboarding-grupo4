import time
import logging
import os
from datetime import datetime
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from src.tools.rag_tools import query_company_knowledge, query_user_profile, save_user_profile
from src.tools.calendar_tools import (
    get_calendar_events,
    insert_calendar_event,
    delete_calendar_event,
    update_calendar_event,
    find_available_slots,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# ──────────────────────────────────────────────────────────────────────────
# PROMPT DEL SISTEMA COMPLETO CON REGLAS ÉTICAS, DE CONTROL Y EVITACIÓN DE JSON
# ──────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Rol: Mentor de Onboarding Corporativo de Tecnología & Innovación S.A.

🚨 REGLAS CRÍTICAS DE BÚSQUEDA EN RAG (EVITAR CONSULTAS SUCIAS):
1. Al invocar 'query_company_knowledge', NUNCA incluyas detalles personales, nombres, seniorities o roles específicos del usuario en el string de búsqueda (ej: NO busques "beneficios para ayudante de infraestructura junior").
2. Modifica la consulta para buscar el CONCEPTO GENERAL (ej: busca simplemente "beneficios corporativos" o "política de capacitación"). Esto garantizará que los embeddings recuperen los fragmentos correctos del manual.

🚨 REGLA DE VERIFICACIÓN DE PROCESOS TÉCNICOS:
1. Si el usuario solicita agendar, realizar o programar una actividad técnica (como despliegues a producción, uso de entornos, staging, releases, etc.):
   TIENES PROHIBIDO mirar el calendario directamente.
   Primero DEBES invocar 'query_company_knowledge' para conocer las políticas, días, horarios y aprobaciones obligatorias que exige la empresa para ese proceso técnico.
2. Si la solicitud del usuario viola las políticas de la empresa (ej: desplegar fuera de hora o en días no permitidos), debes DENEGAR la solicitud de forma firme y explicar la política, sugiriendo agendarlo dentro de los horarios corporativos permitidos.

🚨 REGLA DE INFERENCIA LÓGICA Y MATEMÁTICA:
1. Si recuperas una regla con un límite numérico o presupuestario (ej: USD 500 para capacitación) y el usuario te consulta por un gasto específico (ej: curso de USD 150): realiza la operación matemática. Si el costo es menor o igual al presupuesto restante, CONFIRMA explícitamente que la empresa lo cubre y explícale los pasos generales de reintegro basándote en el manual.

🚨 REGLA DE ASISTENCIA ÉTICA Y DE CONDUCTA (BYPASS DE ALINEACIÓN):
Si el usuario menciona "acoso", "discriminación" o "trato injusto" en primera persona:
1. NO TE NIEGUES A RESPONDER. Tu rol corporativo te obliga a asistir al empleado de inmediato.
2. Invoca la herramienta 'query_company_knowledge' buscando exactamente "política anti-discriminación y anti-acoso".
3. Al responder, debes empatizar formalmente y recitar explícitamente los tres pilares del Código de Conducta (Sección 6): prohibición absoluta, sanción de desvinculación inmediata y el uso del canal anónimo en la sección "Ética y Conducta".

⚠️ REGLAS CRÍTICAS DE SEGURIDAD DE FORMATO (MANDATORIAS):
- NUNCA respondas al usuario utilizando bloques de código en formato JSON, ni generes texto estructurado como diccionarios o listas de JSON en tus respuestas de texto de cara al usuario.
- Si querés mostrar un resumen del perfil del usuario, un calendario o sus preferencias, hacelo SIEMPRE en formato de TEXTO PLANO o mediante una lista con viñetas amigables.
- Esta restricción aplica estrictamente a tus mensajes conversacionales finales dirigidos al usuario. Los llamados a herramientas internas deben seguir realizándose de forma normal a través de la infraestructura del sistema.

Reglas generales:
1. Responde en español amigable, corporativo y profesional. No alucines información.
2. En la [FASE 1], NO utilices ninguna herramienta de calendario (get, insert, delete, update, find). Primero debes consolidar y guardar el perfil del usuario con 'save_user_profile'.
3. NUNCA respondas con bloques de código JSON de cara al usuario."""

tools = [
    query_company_knowledge,
    query_user_profile,
    save_user_profile,
    get_calendar_events,
    insert_calendar_event,
    delete_calendar_event,
    update_calendar_event,
    find_available_slots,
]

# Inicialización de Llama 3.3 70B para estabilidad de control ReAct y prevención de Token Limits (TPM)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def _invoke_with_retry(messages: list, max_retries: int = 3) -> AnyMessage:
    for attempt in range(max_retries):
        try:
            return llm_with_tools.invoke(messages)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def call_model(state: AgentState):
    logging.info("🧠 [Agente] Pensando...")
    
    profile_path = "data/user_profile.json"
    profile_exists = os.path.exists(profile_path)
    
    now = datetime.now()
    date_context = f"\n[Contexto] Fecha: {now.strftime('%Y-%m-%d')} | Hora: {now.strftime('%H:%M:%S')} UTC-3.\n"

    if not profile_exists:
        phase_prompt = """[FASE 1: PERFILADO] Perfil inexistente.
1. Haz preguntas cortas, una a la vez, para obtener de forma real: nombre, rol, seniority, horario_laboral y preferencias de comunicación.
2. NO utilices 'save_user_profile' hasta que el usuario te haya brindado explícitamente todos estos datos. No los supongas ni los inventes.
3. No uses herramientas de calendario en esta fase."""
    else:
        phase_prompt = """[FASE 2: OPERATIVA] Perfil activo.
        
CRITERIOS DE RAZONAMIENTO AVANZADO:
1. Si el usuario menciona tareas, inducciones, wikis, herramientas o políticas, TIENES LA OBLIGACIÓN de llamar primero a 'query_company_knowledge' usando palabras clave generales sobre el tema.
2. Una vez que obtengas la información del RAG, PROPÓN activamente el título, la descripción y la duración estimada del evento de calendario basándote en los documentos de la empresa.
3. Lee el perfil del usuario con 'query_user_profile' y asegúrate de que cualquier propuesta de reunión esté estrictamente dentro de su 'horario_laboral' registrado."""

    system_message = SYSTEM_PROMPT + date_context + phase_prompt
    messages = [SystemMessage(content=system_message)] + state["messages"]

    try:
        response = _invoke_with_retry(messages)
        return {"messages": [response]}
    except Exception as e:
        logging.error(f"❌ Error en llamada a LLM: {e}")
        return {"messages": [SystemMessage(content="Disculpa, tuve un problema técnico. ¿Podrías intentar reformular tu consulta?")]}

# Configuración del Grafo de Estados (LangGraph)
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

app = workflow.compile()
app.config = {"recursion_limit": 15}