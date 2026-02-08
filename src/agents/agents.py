from google.adk.agents import SequentialAgent, LlmAgent
from src.tools.tools import rag_tool, search_tool
from src.observability.monitor import log_agent_execution
import os

# Refusal Message Template
REFUSAL_MSG = "Sorry, I am only trained in sports area. Other than outdoor sports, I do not have knowledge or expertise."

class OrchestratorAgent(SequentialAgent):
    """
    Main Orchestrator that routes queries and coordinates the workflow.
    """
    def __init__(self, **kwargs):
        super().__init__(
            name="Orchestrator",
            description="Interprets user intent and supervises the response generation.",
            **kwargs
        )

class ResearcherAgent(LlmAgent):
    """
    Specialized agent for finding information via RAG or Web Search.
    """
    def __init__(self, **kwargs):
        super().__init__(
            name="Researcher",
            description="Finds answers for sports questions using RAG (Tennis/Cricket) or Web Search.",
            instruction="""You are a sports researcher. 
            If the question is about Tennis or Cricket, use the 'query_tennis_cricket_rag_tool'.
            If the question is about other outdoor sports (like Soccer, Baseball, etc.), use the 'web_sports_search_tool'.
            Always provide a factual, detailed answer based on the tool output.
            IMPORTANT: You MUST explicitly mention the source of your information in your response. 
            For RAG, mention the specific file (e.g., 'Source: tennis.pdf'). 
            For Web Search, mention 'Source: Internet (Tavily)'.
            If you cannot find information, state that clearly.""",
            tools=[rag_tool, search_tool],
            **kwargs
        )

class ReviewerAgent(LlmAgent):
    """
    Specialized agent for Quality Assurance and validation.
    """
    def __init__(self, **kwargs):
        super().__init__(
            name="Reviewer",
            description="Reviews the researcher's output for accuracy and adherence to sports-only rules.",
            instruction="""You are a sports review expert. 
            Your job is to review the answer provided by the Researcher.
            Ensure the answer is accurate, well-formatted, and strictly about sports.
            CRITICAL: Check that the final response includes an explicit source citation (e.g., 'Source: cricket.pdf' or 'Source: Internet (Tavily)').
            If the citation is missing, add it based on the researcher's evidence.
            If the answer is good, you can simply pass it through or refine it for clarity.
            If the answer is not sports-related, refuse to answer using the following message:
            "Sorry, I am only trained in sports area. Other than outdoor sports, I do not have knowledge or expertise." """,
            **kwargs
        )
