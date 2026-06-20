from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from src.tools.rag_tools import query_company_knowledge
from src.tools.calendar_tools import get_calendar_events, insert_calendar_event

# 1. Definir Estado
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Configurar LLM y Tools
tools = [query_company_knowledge, get_calendar_events, insert_calendar_event]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

sys_prompt = SystemMessage(content="Eres un Mentor de Onboarding. Usa el RAG para políticas y Calendar para agendar.")

# 3. Nodos del Bucle ReAct
def agent_node(state: AgentState):
    response = llm_with_tools.invoke([sys_prompt] + state["messages"])
    return {"messages": [response]}

# 4. Construir Grafo
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

app = workflow.compile()