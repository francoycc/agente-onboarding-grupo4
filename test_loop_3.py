import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv(override=True)

# Simular las herramientas vacías
def query_user_profile(query: str): return "El perfil del usuario aún no ha sido creado."
def save_user_profile(profile_data_json: str): return "Guardado"

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

tools = [query_user_profile, save_user_profile]
llm_with_tools = llm.bind_tools(tools)

messages = [
    SystemMessage(content="[FASE 1: PERFILADO] Perfil inexistente. Haz preguntas cortas. No uses otras tools hasta crear el perfil."),
    HumanMessage(content="Hola buenas tardes, mi nombre es valentino, desarrollador junior, nuevo en la empresa!")
]

try:
    response = llm_with_tools.invoke(messages)
    if response.tool_calls:
        print("LLM Tool Calls:", response.tool_calls)
    print("LLM Content:", response.content)
except Exception as e:
    print("ERROR:", str(e))
