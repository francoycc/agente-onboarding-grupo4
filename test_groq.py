import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

load_dotenv(override=True)

@tool
def save_user_profile(profile_data_json: str) -> str:
    """Guarda el perfil del usuario."""
    return "Perfil guardado."

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
llm_with_tools = llm.bind_tools([save_user_profile])

messages = [
    SystemMessage(content="Sos un asistente de onboarding. Hacé preguntas cortas para conocer al empleado."),
    HumanMessage(content="Hola buenas tardes, mi nombre es valentino, desarrollador junior, nuevo en la empresa!")
]

try:
    response = llm_with_tools.invoke(messages)
    print("SUCCESS")
    print("Tool calls:", response.tool_calls if response.tool_calls else "Ninguno")
    print("Content:", response.content[:300] if response.content else "(vacío)")
except Exception as e:
    print("ERROR:", str(e)[:500])
