import os
import requests
from google.adk.tools import FunctionTool
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.utilities import GoogleSearchAPIWrapper
from dotenv import load_dotenv

load_dotenv()

# Global instances for lazy loading
_embeddings = None
_vector_db = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
    return _embeddings

def get_vector_db():
    global _vector_db
    if _vector_db is None and os.path.exists("faiss_index"):
        try:
            print("Loading FAISS index...", flush=True)
            _vector_db = FAISS.load_local("faiss_index", get_embeddings(), allow_dangerous_deserialization=True)
            print("FAISS index loaded successfully.", flush=True)
        except Exception as e:
            print(f"Error loading FAISS index: {e}", flush=True)
    return _vector_db

def warmup():
    """Forces loading of embeddings and vector DB at startup."""
    print("Warming up resources...", flush=True)
    get_embeddings()
    get_vector_db()
    print("Warmup complete.", flush=True)

def query_tennis_cricket_rag(query: str):
    """Answers questions specifically about Tennis and Cricket based on local PDFs."""
    db = get_vector_db()
    if not db:
        return "The sports knowledge base is not initialized. Please wait for the system to process the knowledge base."
    
    docs = db.similarity_search(query, k=3)
    results = []
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown local document')
        # Use only the filename for cleaner display
        source_name = os.path.basename(source)
        results.append(f"[Source: {source_name}]\n{doc.page_content}")
    
    return "\n\n---\n\n".join(results)

def web_sports_search(query: str):
    """Searches the web for information about outdoor sports other than Tennis and Cricket."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "The Tavily Search tool is not configured. Please set TAVILY_API_KEY to enable this feature."
    
    try:
        # Using requests directly to avoid dependency issues locally
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Format the response to be readable by the agent
        results = []
        for result in data.get('results', []):
            results.append(f"[Source: Internet (Tavily) - {result.get('url')}]\n{result.get('content')}")
        
        if not results:
            return "No search results found for this query."
            
        return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"Error performing Tavily search via API: {str(e)}"

# Define Tools for ADK Agents
# Note: FunctionTool uses the function's name and docstring for the tool's name and description.

def query_tennis_cricket_rag_tool(query: str):
    """Useful for answering questions about Tennis and Cricket specifically."""
    print(f"--- AGENT ACTION: Researcher is querying local knowledge base (RAG) for: '{query}' ---")
    result = query_tennis_cricket_rag(query)
    # Extract source filenames for logging
    sources = [line for line in result.split("\n") if "[Source:" in line]
    if sources:
        print(f"--- RAG RESULT: Found relevant info in {len(sources)} document chunks. Sources: {', '.join(sources[:2])}... ---")
    else:
        print("--- RAG RESULT: No specific matches found in local knowledge base. ---")
    return result

def web_sports_search_tool(query: str):
    """Useful for answering questions about outdoor sports that are NOT Tennis or Cricket."""
    print(f"--- AGENT ACTION: Researcher is performing Web Search (Tavily) for: '{query}' ---")
    result = web_sports_search(query)
    if "Result:" in result or "[Source:" in result:
        print("--- WEB RESULT: Successfully retrieved data from Internet via Tavily. ---")
    else:
        print(f"--- WEB RESULT: Search completed with status: {result[:50]}... ---")
    return result

rag_tool = FunctionTool(func=query_tennis_cricket_rag_tool)
search_tool = FunctionTool(func=web_sports_search_tool)
