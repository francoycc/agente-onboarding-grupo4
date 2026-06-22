# ingest.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def ingest_knowledge():
    print("Cargando documentos...")
    # 1. Cargar el documento
    loader = TextLoader("data/manual_onboarding.txt", encoding="utf-8")
    docs = loader.load()

    # 2. Dividir en fragmentos (Chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)

    # 3. Crear embeddings y guardar en ChromaDB local
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory="./chroma_db"
    )
    print(f"¡Éxito! Se guardaron {len(splits)} fragmentos en ChromaDB.")

if __name__ == "__main__":
    ingest_knowledge()