# ingest.py
import os
import logging
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def ingest_knowledge():
    logging.info("1. Iniciando carga de documentos...")
    
    # Verifica que el archivo exista
    file_path = "data/manual_onboarding.txt"
    if not os.path.exists(file_path):
        logging.error(f"El archivo {file_path} no existe. Créalo y ponle texto.")
        return

    # 1. Cargar el documento
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    logging.info(f"Documento cargado. Longitud: {len(docs[0].page_content)} caracteres.")

    # 2. Dividir en fragmentos (Chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    logging.info(f"Documento dividido en {len(splits)} fragmentos.")

    # 3. Crear embeddings y guardar en ChromaDB
    logging.info("Descargando modelo de Embeddings multilingüe (esto puede demorar la primera vez)...")
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    
    logging.info("Creando base de datos vectorial ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory="./chroma_db" # Aquí se guardará la base de datos
    )
    logging.info("¡Éxito! Base de datos ChromaDB configurada y poblada correctamente.")

if __name__ == "__main__":
    ingest_knowledge()