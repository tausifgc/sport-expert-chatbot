# Sport Expert - Multi-Agent Intelligence System 🎾🏏

A production-ready **Multi-Agent System** that answers sports questions by intelligently combining information from a local **RAG knowledge base** (for Tennis & Cricket) and live **Web Search** (for other sports) using the **Google Agent Development Kit (ADK)** and **Gemini 2.0 Flash**.

## 🚀 Features

*   **Intelligent Routing**: Automatically decides whether to check local documents or search the web based on the query.
*   **Sequential Agents**: 
    1.  **Researcher Agent**: Finds the best answer using specialized tools.
    2.  **Reviewer Agent**: Validates accuracy, enforces sports-only policy, and ensures source citation.
*   **Transparent Sourcing**: Every answer includes a clear citation (e.g., `Source: Tennis.pdf` or `Source: Internet (Tavily)`).
*   **Production Deployment**: Fully containerized and deployed on **Google Cloud Run**.

## 🛠 Tech Stack

*   **Framework**: [Google ADK](https://github.com/google/agent-development-kit) (Agent Development Kit)
*   **LLM**: Gemini 2.0 Flash (`gemini-2.0-flash`) via Google Vertex AI.
*   **Vector Database**: FAISS (local index for RAG).
*   **Web Search**: Tavily Search API (optimized for LLMs).
*   **Backend**: Flask + Gunicorn.
*   **Frontend**: Vanilla HTML/JS with real-time updates.

## 📂 Project Structure

```text
MultiAgentAssignment/
├── knowledge_base/         # Source PDFs
│   ├── cricket.pdf
│   └── Tennis.pdf
├── faiss_index/            # Generated Vector Store
├── src/
│   ├── agents/
│   │   └── agents.py       # Orchestrator, Researcher, Reviewer logic
│   ├── tools/
│   │   └── tools.py        # RAG & Tavily Search Tool implementations
│   ├── rag/
│   │   └── ingest.py       # Script to digest PDFs into FAISS
│   ├── observability/
│   │   └── monitor.py      # Custom logging decorators
│   ├── ui/                 # Frontend assets (index.html, script.js)
│   └── main.py             # Flask API Entry Point
├── deployment/             # All deployment-related files
│   ├── deploy-cloud-build.sh    # Cloud Build deployment script
│   ├── cloud-run-config.yaml    # Cloud Run service configuration
│   ├── Dockerfile.base          # Base image Dockerfile
│   └── Dockerfile.ui            # UI container Dockerfile
├── Presentation/           # Project presentation materials
│   ├── Multi-Agent-Sports-Intelligence-System-By-Tausif.pdf
│   └── Multi-Agent-Sports-Intelligence-System-By-Tausif.mp4
├── tests/                  # Test files
├── data/                   # Additional data files
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── deploy.sh               # Quick deploy script
├── setup-github.sh         # GitHub repository setup script
├── Dockerfile              # Production container config
├── requirements.txt        # Python dependencies
├── README.md               # You are here
├── WALKTHROUGH.md          # Implementation walkthrough
├── PERFORMANCE_OPTIMIZATION.md  # Performance tuning guide
└── GITHUB_SETUP.md         # GitHub setup instructions
```

## ⚡ Quick Start (Local)

### Prerequisites
*   Python 3.10+
*   Google Cloud Project with Vertex AI enabled
*   Tavily API Key

### 1. Setup Environment
```bash
# Clone the repo
git clone <repo-url>
cd MultiAgentAssignment

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
Create a `.env` file or export variables directly:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export TAVILY_API_KEY="tvly-..."
```

### 3. Build Knowledge Base
Process the PDF files into a vector index:
```bash
python3 src/rag/ingest.py
```

### 4. Run the Application
Start the backend server:
```bash
python3 src/main.py
```
Then open `http://localhost:8080` (or open `src/ui/index.html` directly to chat).

## ☁️ Deployment (Google Cloud Run)

This project is optimized for Cloud Run deployment with performance optimizations.

### Quick Deploy (Recommended)
```bash
./deploy.sh
```

This will:
- Build the Docker image using Google Cloud Build
- Deploy to Cloud Run with optimized settings:
  - 2 vCPUs, 2GB RAM
  - Min instances: 1 (no cold starts)
  - CPU boost enabled
  - 120s timeout

### Manual Deploy
```bash
./deployment/deploy-cloud-build.sh
```

Or using gcloud directly:
```bash
gcloud run deploy sport-expert-chatbot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --set-env-vars TAVILY_API_KEY=your-key,GOOGLE_CLOUD_PROJECT=your-project,GOOGLE_GENAI_USE_VERTEXAI=True
```

See [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) for details on performance tuning.

## 🔍 Observability

Logs are structured for clarity. In **Cloud Logging**, look for:
*   `>>> NEW REQUEST`: A new user query.
*   `--- AGENT ROLE`: Which agent is currently "thinking".
*   `--- AGENT ACTION`: Tools being used (RAG vs. Search).
*   `>>> REVIEWER`: Final validation and approval.

---
**Developed by Antigravity**
