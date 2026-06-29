import os
from dotenv import load_dotenv
load_dotenv()

# Forzar logs detallados de langchain
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from src.core.agent import app
from langchain_core.messages import HumanMessage

def run_diagnose():
    print("🔍 Iniciando Diagnóstico de Agente en Consola...")
    
    # 1. Verificar si existen las credenciales y el token
    print(f"📁 ¿Existe credentials.json?: {os.path.exists('credentials.json')}")
    print(f"📁 ¿Existe token.json?: {os.path.exists('token.json')}")
    print(f"📁 ¿Existe la base chroma_db?: {os.path.exists('chroma_db')}")
    print(f"📁 ¿Existe el perfil de usuario?: {os.path.exists('data/user_profile.json')}")
    
    # 2. Query que causa la congelación
    query = "Basándome en las políticas de la empresa, estuve recibiendo tratos de discriminación y acoso, ¿cómo se maneja la empresa frente a estas situaciones?"
    
    inputs = {"messages": [HumanMessage(content=query)]}
    
    print("\n🚀 Enviando consulta al grafo LangGraph...")
    try:
        # Ejecutamos el streaming para ver qué nodo se activa y qué devuelve
        for event in app.stream(inputs):
            for node_name, output in event.items():
                print(f"\n📍 [Nodo Activado: {node_name}]")
                messages = output.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    print(f"💬 Tipo de Mensaje: {type(last_msg).__name__}")
                    print(f"📝 Contenido: {last_msg.content}")
                    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                        print(f"🛠️ Llamada a herramientas: {last_msg.tool_calls}")
    except Exception as e:
        print(f"\n❌ Se produjo una excepción durante el flujo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnose()