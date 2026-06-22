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