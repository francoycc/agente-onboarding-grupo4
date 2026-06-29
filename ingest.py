import os
import shutil
import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configuración de logs detallados
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_knowledge():
    logging.info("1. Iniciando carga de documentos...")
    
    file_path = "data/manual_onboarding.txt"
    if not os.path.exists(file_path):
        logging.error(f"El archivo {file_path} no existe en la ruta especificada.")
        return

    # 1. Cargar el manual de onboarding
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    logging.info(f"Documento cargado. Longitud: {len(docs[0].page_content)} caracteres.")

    # 2. Dividir en fragmentos (Chunks) optimizados
    # Subimos chunk_size para evitar fragmentar listas lógicas (Sección 5: Beneficios, Sección 8: Scrum)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    splits = text_splitter.split_documents(docs)
    logging.info(f"Documento dividido en {len(splits)} fragmentos semánticos.")

    # 3. Limpieza de base de datos anterior
    db_path = "./chroma_db"
    if os.path.exists(db_path):
        logging.info("Limpiando base de datos ChromaDB anterior para evitar colisiones...")
        try:
            shutil.rmtree(db_path)
            logging.info("Carpeta 'chroma_db' eliminada con éxito.")
        except Exception as e:
            logging.warning(f"No se pudo eliminar de forma automática: {e}. Asegúrate de cerrar Streamlit.")

    # 4. Descargar y configurar modelo de embeddings multilingüe
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 5. Población de ChromaDB con métrica COSINE (BUG #1 FIX)
    # Declaramos explícitamente "cosine" en los metadatos de la colección.
    # Esto soluciona el desordenamiento vectorial causado por la distancia L2 por defecto de Chroma.
    logging.info("Creando y poblando base de datos vectorial ChromaDB con métrica COSINE...")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=db_path,
        collection_metadata={"hnsw:space": "cosine"}  # <-- FIX CRÍTICO
    )
    logging.info("¡Éxito absoluto! Base de datos ChromaDB configurada con métrica Coseno real.")

if __name__ == "__main__":
    ingest_knowledge()