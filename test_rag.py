import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

db = Chroma(persist_directory='c:/Users/Valentino/Desktop/TP-IA/agente-onboarding-grupo4-main/chroma_db', embedding_function=HuggingFaceEmbeddings(model_name='paraphrase-multilingual-MiniLM-L12-v2'))
docs = db.max_marginal_relevance_search('beneficios de trabajar en la empresa', k=4, fetch_k=10)

with open('c:/Users/Valentino/Desktop/TP-IA/agente-onboarding-grupo4-main/rag_test_mmr.txt', 'w', encoding='utf-8') as f:
    f.write('\n---\n'.join([d.page_content for d in docs]))
