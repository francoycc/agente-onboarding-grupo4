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
    """Busca en los manuales de la empresa, políticas de RRHH, procesos de desarrollo, herramientas y rutas de aprendizaje. 
    Input: una frase de búsqueda clara en español sobre lo que el empleado necesita saber."""
    try:
        db = _get_chroma_db()
        
        # Buscamos los 5 fragmentos lógicos más cercanos vectorialmente
        results = db.similarity_search_with_relevance_scores(query, k=5)
        
        if not results:
            return "No se encontró información relevante en los manuales corporativos."
        
        # ──────────────────────────────────────────────────────────────────────
        # CALIBRACIÓN DE UMBRAL (MÉTRICA COSENO)
        # Ajustamos el umbral a 35% (0.35) para evitar falsos negativos en frases 
        # conceptuales cortas (misión, visión, beneficios) sin dejar entrar ruido.
        # ──────────────────────────────────────────────────────────────────────
        threshold = 0.35
        
        formatted_docs = []
        for idx, (doc, score) in enumerate(results, start=1):
            if score < threshold:
                continue
                
            source_path = doc.metadata.get("source", "manual_onboarding.txt")
            source_file = os.path.basename(source_path)
            
            formatted_docs.append(
                f"[Fragmento {idx}] (Fuente: {source_file} | Relevancia: {score:.2%})\n"
                f"Contenido: {doc.page_content.strip()}"
            )
            
        if not formatted_docs:
            return (
                f"Se encontraron coincidencias semánticas en los manuales, pero ninguna supera "
                f"el umbral de confianza mínimo del {threshold:.0%} de similitud (Métrica Coseno)."
            )
            
        context = "\n\n".join(formatted_docs)
        return f"Información recuperada de la base de conocimiento corporativa:\n\n{context}"
        
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