import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def ingest_docs():
    data_path = "knowledge_base/"
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"Created {data_path} directory. Please add your Tennis and Cricket PDFs there.")
        return

    loader = PyPDFDirectoryLoader(data_path)
    documents = loader.load()
    
    if not documents:
        print("No documents found in data/ directory.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # Use VertexAI embeddings
    from langchain_google_vertexai import VertexAIEmbeddings
    embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
    
    vector_db = FAISS.from_documents(texts, embeddings)
    vector_db.save_local("faiss_index")
    print("FAISS index created and saved to 'faiss_index'")

if __name__ == "__main__":
    ingest_docs()
