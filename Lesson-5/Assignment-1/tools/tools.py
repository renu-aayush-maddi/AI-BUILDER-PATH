from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

# from tools.documents import IT_DOCS, FINANCE_DOCS
from tools.documents import DOCUMENTS


# @tool
# def read_it_document(filename: str) -> str:
#     """Read IT internal documentation."""
#     return IT_DOCS.get(filename,f"IT file {filename} not found")


# @tool
# def read_finance_document(filename: str) -> str:
#     """Read Finance internal documentation."""
#     return FINANCE_DOCS.get(filename,f"Finance file {filename} not found")


@tool
def read_document(department: str,filename: str) -> str:
    """Read internal company documentation."""

    docs = DOCUMENTS.get(department)

    if not docs:
        return f"Unknown department {department}"

    return docs.get(filename,f"{department} file {filename} not found")


web_search = TavilySearch(max_results=3,search_depth="basic",name="web_search")