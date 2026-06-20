import logging
from dotenv import load_dotenv
from src.core.agent import app

# Cargar variables de entorno
load_dotenv()

# Configurar Logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("Agente de Onboarding Iniciado. Escriba 'salir' para terminar.")
    while True:
        user_input = input("\nUsuario: ")
        if user_input.lower() in ['salir', 'exit', 'quit']:
            break
        
        logging.info("Iniciando procesamiento de turno...")
        for event in app.stream({"messages": [("user", user_input)]}):
            for value in event.values():
                if "messages" in value:
                    msg = value["messages"][-1]
                    if msg.type == "ai" and not msg.tool_calls:
                        print(f"\nAgente: {msg.content}")
                    elif msg.type == "ai" and msg.tool_calls:
                        logging.info(f"El Agente decidió usar herramientas: {[t['name'] for t in msg.tool_calls]}")

if __name__ == "__main__":
    main()