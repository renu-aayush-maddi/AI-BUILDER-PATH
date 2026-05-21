import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from langchain_community.tools.tavily_search import TavilySearchResults



load_dotenv()

mcp = FastMCP("web-search-server")

MAX_RESULTS = 5

tavily_tool = TavilySearchResults(
    max_results=MAX_RESULTS,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=False,
    include_images=False,
)


@mcp.tool()
def web_search(query: str) -> str:

    try:
        results = tavily_tool.invoke(query)

        if not results:
            return "No web results found."

        if isinstance(results, str):
            return results

        formatted = []

        for i, r in enumerate(results, 1):

            title = r.get("title", "")
            url = r.get("url", "")
            content = r.get("content", "")

            formatted.append(
                f"[{i}] {title}\n{url}\n{content}"
            )

        return "\n\n".join(formatted)

    except Exception as e:

        return f"Web Search Error: {e}"


if __name__ == "__main__":

    mcp.run()