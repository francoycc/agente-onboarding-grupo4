import os
import json
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ──────────────────────────────────────────────────────────────────────────
# ARQUITECTURA DE RENDIMIENTO (SINGLETON PATTERN)
# Cargar el modelo de embeddings y la base Chroma una única vez en memoria.
# Esto reduce drásticamente el tiempo de respuesta y evita fugas de memoria.
# ──────────────────────────────────────────────────────────────────────────
_EMBEDDINGS_MODEL = None
_CHROMA_DB = None

def _get_chroma_db():
    """Función interna que implementa Lazy Loading para reutilizar las instancias
    del modelo y de la base de datos con normalización geométrica de vectores."""
    global _EMBEDDINGS_MODEL, _CHROMA_DB
    
    if _EMBEDDINGS_MODEL is None:
        # Cargamos el modelo con normalización de longitud vectorial (longitud = 1)
        # Sincronizado con ingest.py
        _EMBEDDINGS_MODEL = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            encode_kwargs={'normalize_embeddings': True}
        )
        
    if _CHROMA_DB is None:
        _CHROMA_DB = Chroma(
            persist_directory="./chroma_db", 
            embedding_function=_EMBEDDINGS_MODEL
        )
        
    return _CHROMA_DB

@tool
def query_company_knowledge(query: str) -> str:
    """Busca en los manuales de la empresa, políticas de RRHH y rutas de aprendizaje.
    Input: una frase de búsqueda clara sobre lo que el empleado necesita saber.
    Regla: Si encuentras múltiples tareas, devuélvelas todas explícitamente."""
    try:
        # 1. Configuración persistente (Ruta absoluta)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        persist_directory = os.path.join(base_dir, "chroma_db")
        embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        
        # 2. Búsqueda con relevancia
        results = db.similarity_search_with_relevance_scores(query, k=5)
        
        if not results:
            return "CONTEXTO_NO_ENCONTRADO: No existe información en el manual para esa consulta."

        # 3. Filtrado por Umbral (Threshold)
        threshold = 0.35
        filtered_docs = [doc for doc, score in results if score >= threshold]
        
        if not filtered_docs:
            return f"Se encontraron coincidencias, pero ninguna supera el umbral de confianza ({threshold})."

        # 4. Formateo con la nueva instrucción de "Planificación Voraz"
        # Aquí forzamos al modelo a ver cada ítem como una tarea individual obligatoria
        context = "\n\n".join([f"- TAREA OBLIGATORIA: {doc.page_content.strip()}" for doc in filtered_docs])
        
        return f"DATOS_DEL_MANUAL:\n{context}\n\nREGLA: Usa solo estos datos para responder. No añadas información externa."
        
    except Exception as e:
        return f"Error al consultar la base de conocimiento: {str(e)}"


@tool
def query_user_profile(query: str) -> str:
    """Recupera el perfil de rutina, rol, seniority y preferencias del usuario.
    Input: Frase de búsqueda o consulta sobre el perfil del usuario."""
    try:
        file_path = "data/user_profile.json"
        if not os.path.exists(file_path):
            return "El perfil del usuario aún no ha sido creado. Es necesario realizar la entrevista de onboarding primero."
        
        with open(file_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
            
        return f"Perfil y Rutina del Usuario Registrada:\n{json.dumps(profile_data, indent=2, ensure_ascii=False)}"
    except Exception as e:
        return f"Error al recuperar el perfil del usuario: {str(e)}"


@tool
def save_user_profile(profile_data_json: str) -> str:
    """Guarda el perfil del usuario en la base de datos local una vez finalizada la entrevista de inducción.
    Input: Un string JSON con la información estructurada: nombre, rol, seniority, horario_laboral, y preferencias."""
    try:
        data = json.loads(profile_data_json)
        os.makedirs("data", exist_ok=True)
        with open("data/user_profile.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return "¡Éxito! El perfil de usuario ha sido guardado correctamente. La Fase 1 (Descubrimiento y Perfilado) ha finalizado."
    except Exception as e:
        return f"Error al guardar el perfil: {str(e)}. Asegúrate de pasar un JSON válido."