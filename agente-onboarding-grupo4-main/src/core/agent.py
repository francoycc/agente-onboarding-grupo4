# src/core/agent.py
import time
import logging
import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
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

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

SYSTEM_PROMPT = """Sos el Asistente de Onboarding de Tecnología & Innovación S.A.

=== REGLA ABSOLUTA: GROUNDING DEL MANUAL ===
Cuando uses 'query_company_knowledge', el texto que recibás entre [INICIO_MANUAL] y [FIN_MANUAL] ES la única fuente de verdad.
TU RESPUESTA DEBE:
  - Basarse exclusivamente en ese texto. Copiá y organizá la información que el texto dice.
  - Si algo NO está en ese texto, NO lo incluyas. Jamás agregues información de tu conocimiento general.
  - Si la pregunta del usuario no puede responderse con el texto recuperado, decí: 'El manual no contiene información sobre ese tema.'

EJEMPLO CORRECTO:
Texto del manual: 'BENEFICIOS: - OSDE 410 al 70% - Bono 15%'
Respuesta: 'Según el manual, los beneficios son: OSDE 410 bonificada al 70% y bono anual del 15%.'

EJEMPLO INCORRECTO (PROHIBIDO):
Texto del manual: 'BENEFICIOS: - OSDE 410 al 70%'
Respuesta: 'Además de OSDE, contamos con cultura de colaboración y excelencia técnica...' <- ESTO ES INVENTAR

=== REGLAS OPERATIVAS ===
1. Responde en español amigable y profesional.
2. Para CUALQUIER pregunta sobre la empresa (estructura, beneficios, procesos, herramientas, cultura), usá SIEMPRE 'query_company_knowledge' antes de responder. Nunca respondas de memoria.
3. Cuando uses el tool, pasá palabras clave cortas y exactas: 'beneficios', 'estructura empresa', 'herramientas', 'horario laboral', 'codigo conducta', etc.
4. Jamás respondas sobre la empresa sin antes consultar el manual.

Calendario — reglas:
- ELIMINAR evento: usá 'delete_calendar_event'.
- MODIFICAR evento: usá 'update_calendar_event'.
- CREAR evento: revisá disponibilidad con 'get_calendar_events' o 'find_available_slots', luego usá 'insert_calendar_event'.
- NUNCA agendes en el pasado."""

# ──────────────────────────────────────────────────────────
# Herramientas separadas por fase para evitar que el LLM
# invoque tools incorrectas en la fase equivocada
# ──────────────────────────────────────────────────────────
PHASE1_TOOLS = [save_user_profile]

PHASE2_TOOLS = [
    query_company_knowledge,
    query_user_profile,
    save_user_profile,
    get_calendar_events,
    insert_calendar_event,
    delete_calendar_event,
    update_calendar_event,
    find_available_slots,
]

# Todas las tools deben estar en el ToolNode para que pueda ejecutar cualquiera
ALL_TOOLS = PHASE2_TOOLS

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)


# ──────────────────────────────────────────────────────────
# RETRY con backoff exponencial para errores de rate limit
# ──────────────────────────────────────────────────────────
def _invoke_with_retry(llm_bound, messages: list, max_retries: int = 3) -> AnyMessage:
    """Invoca el LLM con reintentos automáticos ante errores de rate limit (429)
    o fallos de tool_use (400). Usa backoff exponencial."""
    for attempt in range(max_retries):
        try:
            return llm_bound.invoke(messages)
        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = "429" in err_str or "rate_limit" in err_str or "rate limit" in err_str
            is_tool_fail  = "400" in err_str or "tool_use_failed" in err_str

            if (is_rate_limit or is_tool_fail) and attempt < max_retries - 1:
                wait_sec = 2 ** attempt  # 1s, 2s, 4s
                logging.warning(
                    f"⚠️ Error Groq (intento {attempt + 1}/{max_retries}): {e}. "
                    f"Reintentando en {wait_sec}s..."
                )
                time.sleep(wait_sec)
            else:
                raise


def call_model(state: AgentState):
    from datetime import datetime
    logging.info("🧠 [Agente] Pensando...")

    profile_exists = os.path.exists("data/user_profile.json")

    now = datetime.now()
    date_context = (
        f"\n[Contexto Temporal]\n"
        f"- Fecha actual: {now.strftime('%Y-%m-%d')}\n"
        f"- Hora actual: {now.strftime('%H:%M:%S')}\n"
        f"- Zona Horaria: UTC-3 (Argentina)\n"
        f"CRÍTICO: Si el usuario usa términos relativos como 'mañana a la tarde' o 'hoy a las 15', DEBES interpretarlos asumiendo esta fecha, hora y zona horaria (UTC-3). Nunca agendes en el pasado.\n"
    )

    if not profile_exists:
        phase_prompt = """\n[FASE 1: PERFILADO] Perfil inexistente.
Tu ÚNICO objetivo ahora es recopilar la información del nuevo empleado.
1. Hacé preguntas cortas, de a una por vez, para obtener: nombre, rol, seniority, horario y preferencias.
2. Cuando tengas TODOS los datos, usá 'save_user_profile' con un JSON que tenga: nombre, rol, seniority, horario_laboral, preferencias.
3. NO tenés acceso a otras herramientas en esta fase. Solo podés conversar y usar 'save_user_profile'."""
        current_tools = PHASE1_TOOLS
    else:
        phase_prompt = """\n[FASE 2: OPERATIVA] Perfil activo.
1. Para CUALQUIER pregunta sobre la empresa (estructura, beneficios, procesos), usá 'query_company_knowledge' con palabras clave cortas (ej: 'estructura', 'beneficios'). NUNCA uses frases largas.
2. Para agendar, leé 'query_user_profile' y revisá la agenda ('get_calendar_events', 'find_available_slots').
3. Para eliminar eventos, usá 'delete_calendar_event'. Para modificar, usá 'update_calendar_event'.
4. Si hay conflicto, NO agendes; usá 'find_available_slots' para buscar opciones.
5. Si está libre, usá 'insert_calendar_event'."""
        current_tools = PHASE2_TOOLS

    # Bindear SOLO las tools de la fase actual al LLM
    llm_with_phase_tools = llm.bind_tools(current_tools)

    system_message = SYSTEM_PROMPT + date_context + phase_prompt
    messages = [SystemMessage(content=system_message)] + state["messages"]

    response = _invoke_with_retry(llm_with_phase_tools, messages)

    if response.tool_calls:
        tool_names = [t["name"] for t in response.tool_calls]
        logging.info(f"🛠️ [Acción] El agente invocó: {tool_names}")

    return {"messages": [response]}


# ──────────────────────────────────────────────────────────
# Grafo LangGraph con límite de iteraciones
# ──────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(ALL_TOOLS))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

# recursion_limit evita bucles infinitos agente↔tools (default: 25)
app = workflow.compile()
app.config = {"recursion_limit": 15}