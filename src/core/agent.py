# src/core/agent.py
import logging
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from src.tools.rag_tools import query_company_knowledge
from src.tools.calendar_tools import get_calendar_events, insert_calendar_event

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

SYSTEM_PROMPT = """Eres un Mentor de Onboarding Corporativo. 
1. Usa 'query_company_knowledge' para consultar políticas o cursos. No inventes reglas.
2. Usa 'get_calendar_events' para ver espacios libres antes de agendar.
3. Usa 'insert_calendar_event' para agendar cursos o reuniones."""

tools = [query_company_knowledge, get_calendar_events, insert_calendar_event]

llm = ChatGroq(model="llama3-70b-8192", temperature=0)
llm_with_tools = llm.bind_tools(tools)

def call_model(state: AgentState):
    logging.info("🧠 [Agente] Pensando...")
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        tool_names = [t["name"] for t in response.tool_calls]
        logging.info(f"🛠️ [Acción] El agente invocó: {tool_names}")
        
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

app = workflow.compile()