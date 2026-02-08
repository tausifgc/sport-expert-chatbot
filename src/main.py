from flask import Flask, request, jsonify
from flask_cors import CORS
from src.agents.agents import OrchestratorAgent, ResearcherAgent, ReviewerAgent
from src.rag.ingest import ingest_docs
from google.adk.agents import SequentialAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models import Gemini
from google.genai.types import Content, Part
from dotenv import load_dotenv
import os
import threading
import logging
import sys

# Configure logging to show up in Cloud Run
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(levelname)s %(message)s",
    force=True,   # Ensure we override any existing handlers (gunicorn/flask)
)
logger = logging.getLogger(__name__)

load_dotenv()

# Set Google Cloud Project and Location for ADK/Vertex AI
os.environ['GOOGLE_CLOUD_PROJECT'] = 'coastal-burner-480319-i7'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

def run_ingestion():
    if not os.path.exists("faiss_index"):
        print("FAISS index not found. Starting background ingestion...")
        ingest_docs()
    else:
        print("FAISS index already exists.")

# Start ingestion in the background
threading.Thread(target=run_ingestion, daemon=True).start()

from src.tools.tools import warmup

# Warm up resources (load FAISS/Embeddings) immediately on container start
warmup()

app = Flask(__name__)
# Allow requests from your specific Cloud Run UI URL
CORS(app, resources={r"/*": {"origins": "https://sport-expert-ui-chatbot-997402636968.us-central1.run.app"}})

# Initialize Agents
# Using gemini-2.0-flash as requested (latest next-gen flash model)
model = Gemini(model="gemini-2.0-flash")
researcher = ResearcherAgent(model=model)
reviewer = ReviewerAgent(model=model)

orchestrator = SequentialAgent(
    name="SportExpertOrchestrator",
    sub_agents=[researcher, reviewer],
    description="Orchestrates the Sport Expert flow."
)

# Initialize ADK Runner
runner = Runner(
    app_name="SportExpert",
    agent=orchestrator,
    session_service=InMemorySessionService(),
    auto_create_session=True
)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'GET':
        return jsonify({"message": "Sport Expert Backend is running. Please use POST to send queries."})
    
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Basic intent check for non-sports
    sports_keywords = ["tennis", "cricket", "sport", "game", "player", "match", "rule", "outdoor", "soccer", "football", "baseball"]
    if not any(kw in query.lower() for kw in sports_keywords):
        return jsonify({"answer": "Sorry, I am only trained in sports area. Other than outdoor sports, I do not have knowledge or expertise."})

    try:
        # User and Session IDs are required by the Runner
        user_id = "default_user"
        session_id = f"session_{user_id}"
        
        # Run the agent and collect events
        logger.info(f"\n>>> NEW REQUEST: {query}")
        print(f"🚀 REQUEST RECEIVED: {query}", flush=True)
        events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=Content(role="user", parts=[Part(text=query)])
        )
        
        # Extract the final answer from the events
        answer = ""
        last_author = "System"
        for event in events:
            for event in events:
                # Detect who is speaking
                author = getattr(event, 'author', last_author)
                if author != last_author:
                    logger.info(f"--- AGENT ROLE: {author} is now processing... ---")
                    last_author = author

                # ADK Event model has a 'content' field (google.genai.types.Content)
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts") and event.content.parts:
                        event_text = "".join([p.text for p in event.content.parts if hasattr(p, "text") and p.text])
                        
                        if event_text:
                            answer = event_text
                            # Check if this is reject
                            if "Other than outdoor sports, I do not have knowledge" in event_text:
                                logger.info(f"!!! POLICY REJECTION: {author} refused the query as non-sports. !!!")
                            else:
                                # Log a preview of what the agent found/reviewed
                                logger.info(f"DEBUG: {author} generated/extracted content: {answer[:40].replace(os.sep, '/')}...")
                                if author == "Reviewer":
                                    logger.info(">>> REVIEWER: Response validated and approved for delivery. ✅")
        
        if not answer:
            logger.warning("Warning: Event stream completed but no answer was extracted.")
            # Let's print the last event for debugging
            try:
                print(f"Last event: {event}")
            except:
                pass
            return jsonify({"error": "No response generated by the agent. Check console for details."}), 500
            
        return jsonify({"answer": answer})
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg and "not found" in error_msg.lower():
            return jsonify({
                "error": "Model or Project not found.",
                "details": "Please ensure the Vertex AI API is enabled and your project has access to gemini-2.0-flash.",
                "fix": "Run: gcloud services enable aiplatform.googleapis.com --project coastal-burner-480319-i7"
            }), 500
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
