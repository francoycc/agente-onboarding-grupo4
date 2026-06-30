# src/tools/rag_tools.py
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
# Global variables for lazy loading
_embeddings = None
_db = None

def _get_db():
    """Inicializa la base de datos de manera perezosa (lazy) para que solo se cargue una vez."""
    global _embeddings, _db
    if _db is None:
        # Usamos un modelo multilingüe optimizado para español
        _embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        _db = Chroma(persist_directory="./chroma_db", embedding_function=_embeddings)
    return _db

@tool
def query_company_knowledge(query: str) -> str:
    """Busca en el manual oficial de la empresa. Retorna el texto EXACTO del manual.
    IMPORTANTE: El agente SOLO puede usar la información dentro de los delimitadores [INICIO_MANUAL] y [FIN_MANUAL].
    Input: palabras clave cortas (ej: 'beneficios', 'estructura', 'horario')."""
    try:
        db = _get_db()

        # MMR garantiza diversidad: evita que todos los chunks hablen del mismo tema
        docs = db.max_marginal_relevance_search(query, k=4, fetch_k=15)

        if not docs:
            return (
                "[INICIO_MANUAL]\n"
                "No se encontró información sobre este tema en el manual oficial.\n"
                "[FIN_MANUAL]"
            )

        chunks = []
        for i, doc in enumerate(docs, 1):
            chunks.append(f"--- Fragmento {i} del Manual ---\n{doc.page_content}")

        context = "\n\n".join(chunks)
        return (
            f"[INICIO_MANUAL]\n"
            f"{context}\n"
            f"[FIN_MANUAL]\n"
            f"INSTRUCCIÓN: Responde usando ÚNICAMENTE el texto anterior. No agregues información propia."
        )
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