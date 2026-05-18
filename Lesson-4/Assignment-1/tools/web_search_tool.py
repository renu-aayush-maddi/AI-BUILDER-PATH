"""
tools/web_search_tool.py
─────────────────────────
LangChain Tool that uses Tavily Search API for live web searches.
Used for industry benchmarks, regulatory updates, and trends.
"""

import os
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
MAX_RESULTS = 5


def get_web_search_tool() -> Tool:
    """
    Return a configured LangChain Tool for web search via Tavily.

    Tavily is optimized for factual, research-grade search — perfect for
    regulatory updates, industry benchmarks, and compliance information.
    """
    if not TAVILY_API_KEY:
        # Return a mock tool if no API key is configured
        def mock_search(query: str) -> str:
            return (
                "⚠️ Web search is not configured. "
                "Set TAVILY_API_KEY in your .env file to enable live web search. "
                f"Query was: '{query}'"
            )
        return Tool(
            name="web_search",
            func=mock_search,
            description=(
                "Search the web for industry benchmarks, regulatory updates, trends, "
                "and external information not available in internal documents."
            ),
        )

    # Real Tavily-backed search tool
    tavily_tool = TavilySearchResults(
        max_results=MAX_RESULTS,
        search_depth="advanced",          
        include_answer=True,             
        include_raw_content=False,
        include_images=False,
    )

    def search_web(query: str) -> str:
        """Run a Tavily web search and format results."""
        try:
            results = tavily_tool.invoke(query)
            if not results:
                return f"No web results found for: '{query}'"

            if isinstance(results, str):
                return results  # Tavily returned a direct answer

            formatted = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "No title")
                url = r.get("url", "")
                content = r.get("content", "")
                formatted.append(f"**[{i}] {title}**\nURL: {url}\n{content}")

            return "\n\n---\n\n".join(formatted)
        except Exception as e:
            return f"❌ Web search error: {e}"

    return Tool(
        name="web_search",
        func=search_web,
        description=(
            "Use this tool to search the internet for current information including: "
            "industry hiring benchmarks, AI regulatory updates, market trends, "
            "competitor analysis, compliance frameworks (GDPR, CCPA, NIST, etc.), "
            "and any external data not available in internal Presidio documents. "
            "Input should be a clear, specific search query."
        ),
    )