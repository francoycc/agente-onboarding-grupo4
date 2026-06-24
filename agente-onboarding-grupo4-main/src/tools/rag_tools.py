# src/tools/rag_tools.py
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
@tool
def query_company_knowledge(query: str) -> str:
    """Busca en los manuales de la empresa, políticas de RRHH y rutas de aprendizaje. 
    Input: una frase de búsqueda clara sobre lo que el empleado necesita saber."""
    try:
        # Usamos un modelo Open Source 
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        
        docs = db.similarity_search(query, k=3)
        
        if not docs:
            return "No se encontró información relevante en los manuales."
        
        context = "\n\n".join([doc.page_content for doc in docs])
        return f"Información recuperada de los manuales:\n{context}"
    except Exception as e:
        return f"Error al consultar la base de conocimiento: {str(e)}"

@tool
def query_user_profile(query: str) -> str:
    """Recupera el perfil de rutina, rol, seniority y preferencias del usuario.
    Input: Frase de búsqueda o consulta sobre el perfil del usuario."""
    import os
    import json
    try:
        file_path = "data/user_profile.json"
        if not os.path.exists(file_path):
            return "El perfil del usuario aún no ha sido creado. Es necesario realizar la entrevista de onboarding primero."
        
        with open(file_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
            
        return f"Perfil y Rutina del Usuario:\n{json.dumps(profile_data, indent=2, ensure_ascii=False)}"
    except Exception as e:
        return f"Error al recuperar el perfil del usuario: {str(e)}"

@tool
def save_user_profile(profile_data_json: str) -> str:
    """Guarda el perfil del usuario en la base de datos local una vez finalizada la entrevista de inducción.
    Input: Un string JSON con la información estructurada: nombre, rol, seniority, horario_laboral, y preferencias."""
    import os
    import json
    try:
        data = json.loads(profile_data_json)
        os.makedirs("data", exist_ok=True)
        with open("data/user_profile.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return "¡Éxito! El perfil de usuario ha sido guardado correctamente. La Fase 1 (Descubrimiento y Perfilado) ha finalizado."
    except Exception as e:
        return f"Error al guardar el perfil: {str(e)}. Asegúrate de pasar un JSON válido."