from langchain_core.tools import tool
# Aquí importarán ChromaDB y los Embeddings

@tool
def query_company_knowledge(query: str) -> str:
    """Busca en el manual del empleado y rutas de aprendizaje. 
    Usa esto para saber qué políticas o cursos debe seguir un perfil."""
    # Lógica de ChromaDB
    return "Resultado simulado: El Junior debe hacer el curso de Git."