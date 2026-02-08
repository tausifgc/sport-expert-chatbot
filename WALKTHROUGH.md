# Sport Expert - Implementation Walkthrough

The **Sport Expert** application is a production-ready multi-agent system built with **Google ADK**, **Gemini 2.0 Flash**, and **Tavily Search API**.

## Core Features ✅

- **Reliable RAG**: Answers about Tennis and Cricket are retrieved from local PDF knowledge bases.
- **Enhanced Web Search**: Queries about other sports (Soccer, etc.) are handled via **Tavily Search**, optimized for AI agents.
- **Source Citation**: Every response explicitly states where the information came from (e.g., `Source: cricket.pdf` or `Source: Internet (Tavily)`).
- **Sports-Only Scope**: Agents are instructed to politely refuse non-sports queries.

---

## Local Testing Status

The system has been verified locally with the following inputs:

| Query | Result | Source Cited |
| :--- | :--- | :--- |
| Tennis rules | **Success** | `tennis.pdf` |
| Cricket batting | **Success** | `cricket.pdf` |
| Soccer World Cup | **Success** | `Internet (Tavily)` |
| Cooking recipe | **Refusal** | N/A |

---

## How it Works

1.  **Researcher Agent**: Intelligently selects between the `query_tennis_cricket_rag_tool` and the `web_sports_search_tool` based on the user's query.
2.  **Tavily Tool**: Uses the Tavily API (via `requests` for max compatibility) to gather high-quality external data.
3.  **Reviewer Agent**: Sanitizes the output and ensures the presence of a clear source citation.
4.  **Orchestrator**: Manages the sequence of agent interactions using ADK's `SequentialAgent`.

---

## Configuration

The following environment variables are required for full functionality:
- `TAVILY_API_KEY`: Your Tavily API key.
- `GOOGLE_CLOUD_PROJECT`: Your GCP Project ID (for Vertex AI).
- `GOOGLE_CLOUD_LOCATION`: Your GCP Region.

---
**Developed by Antigravity**
